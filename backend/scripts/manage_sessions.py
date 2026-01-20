"""Manage session files - view, clean, and export."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.storage_manager import StorageManager


def show_menu():
    """Show interactive menu for session management."""
    print("=" * 60)
    print("会话管理工具")
    print("=" * 60)
    print()
    print("选项:")
    print("  1. 查看所有会话")
    print("  2. 查看会话详情")
    print("  3. 删除 7 天前的会话")
    print("  4. 删除 30 天前的会话")
    print("  5. 删除所有会话")
    print("  6. 退出")
    print()
    
    while True:
        try:
            choice = input("请选择 (1-6): ").strip()
            
            if choice == '1':
                print()
                list_sessions()
                print()
            elif choice == '2':
                print()
                run_id = input("输入会话 run_id: ").strip()
                view_session_detail(run_id)
                print()
            elif choice == '3':
                print()
                clean_old_sessions(days=7)
                print()
            elif choice == '4':
                print()
                clean_old_sessions(days=30)
                print()
            elif choice == '5':
                print()
                clean_all_sessions()
                print()
            elif choice == '6':
                print("退出")
                sys.exit(0)
            else:
                print("无效选择，请输入 1-6")
        except KeyboardInterrupt:
            print("\n\n已取消")
            sys.exit(0)


def list_sessions():
    """List all sessions."""
    storage = StorageManager()
    run_ids = storage.list_sessions()
    
    if not run_ids:
        print("没有找到会话")
        return
    
    print("=" * 100)
    print(f"{'Run ID':<40} {'状态':<10} {'浏览器':<10} {'事件数':<8} {'开始时间':<20}")
    print("=" * 100)
    
    for run_id in run_ids:
        session_json = storage.load_session_json(run_id)
        if session_json and 'session' in session_json:
            session = session_json['session']
            start_time = session.get('start_time', '-')
            if start_time != '-':
                try:
                    dt = datetime.fromisoformat(start_time)
                    start_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            print(f"{run_id:<40} {session.get('status', '-'):<10} {session.get('browser_type', '-'):<10} {session.get('event_count', 0):<8} {start_time:<20}")
    
    print("=" * 100)
    print(f"总计: {len(run_ids)} 个会话")


def view_session_detail(run_id: str):
    """View detailed information for a session."""
    storage = StorageManager()
    session_json = storage.load_session_json(run_id)
    
    if not session_json or 'session' not in session_json:
        print(f"会话 {run_id} 不存在")
        return
    
    session = session_json['session']
    events = session_json.get('events', [])
    
    print()
    print("=" * 80)
    print(f"会话详情 - {run_id}")
    print("=" * 80)
    print(f"起始 URL:       {session.get('start_url') or '-'}")
    print(f"状态:           {session.get('status')}")
    print(f"浏览器:         {session.get('browser_type')}")
    print(f"隐身模式:       {'是' if session.get('incognito') else '否'}")
    print(f"用户数据目录:   {session.get('user_data_dir') or '-'}")
    print(f"事件数:         {session.get('event_count', 0)}")
    print(f"开始时间:       {session.get('start_time') or '-'}")
    print(f"结束时间:       {session.get('end_time') or '-'}")
    print("=" * 80)
    
    # Show events
    if events:
        print()
        print(f"最近 {min(10, len(events))} 个事件:")
        print("-" * 80)
        
        for event in events[:10]:
            timestamp = event.get('timestamp', '-')
            if timestamp != '-':
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%H:%M:%S')
                except:
                    pass
            
            page_url = event.get('page_url', '')[:50]
            print(f"  [{event.get('seq', 0):3d}] {timestamp} - {event.get('event_type', ''):<12} {page_url}")
        
        if len(events) > 10:
            print(f"  ... 还有 {len(events) - 10} 个事件")
        
        print("-" * 80)
    
    # Show folder size
    folder_size = storage.get_session_size(run_id)
    print(f"\n文件夹大小: {folder_size / 1024 / 1024:.2f} MB")
    print(f"文件夹路径: {storage.get_session_folder(run_id)}")
    print()


def clean_old_sessions(days: int):
    """Clean sessions older than specified days."""
    storage = StorageManager()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    print(f"清理 {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 之前的会话...")
    print(f"保留最近 {days} 天的会话")
    print()
    
    run_ids = storage.list_sessions()
    old_sessions = []
    total_size = 0
    
    for run_id in run_ids:
        session_json = storage.load_session_json(run_id)
        if session_json and 'session' in session_json:
            session = session_json['session']
            start_time_str = session.get('start_time')
            
            if start_time_str:
                try:
                    start_time = datetime.fromisoformat(start_time_str)
                    if start_time < cutoff_date:
                        size = storage.get_session_size(run_id)
                        old_sessions.append((run_id, session, size))
                        total_size += size
                except:
                    pass
    
    if not old_sessions:
        print("没有需要清理的旧会话")
        return
    
    print(f"找到 {len(old_sessions)} 个旧会话:")
    print()
    
    for run_id, session, size in old_sessions:
        print(f"  {run_id}:")
        print(f"    - 开始时间: {session.get('start_time')}")
        print(f"    - 事件数: {session.get('event_count', 0)}")
        print(f"    - 大小: {size / 1024 / 1024:.2f} MB")
        print()
    
    print(f"总计:")
    print(f"  - 会话数: {len(old_sessions)}")
    print(f"  - 总大小: {total_size / 1024 / 1024:.2f} MB")
    print()
    
    confirm = input("确认删除以上会话? (yes/no): ")
    if confirm.lower() != 'yes':
        print("取消删除")
        return
    
    print()
    print("开始删除...")
    
    for run_id, _, _ in old_sessions:
        if storage.delete_session(run_id):
            print(f"  已删除: {run_id}")
        else:
            print(f"  删除失败: {run_id}")
    
    print()
    print(f"清理完成!")
    print(f"  - 删除了 {len(old_sessions)} 个会话")
    print(f"  - 释放了 {total_size / 1024 / 1024:.2f} MB 空间")


def clean_all_sessions():
    """Clean ALL sessions."""
    storage = StorageManager()
    
    print("清理所有会话...")
    print()
    
    run_ids = storage.list_sessions()
    
    if not run_ids:
        print("没有会话需要清理")
        return
    
    total_size = 0
    sessions_info = []
    
    for run_id in run_ids:
        session_json = storage.load_session_json(run_id)
        if session_json and 'session' in session_json:
            session = session_json['session']
            size = storage.get_session_size(run_id)
            sessions_info.append((run_id, session, size))
            total_size += size
    
    print(f"找到 {len(sessions_info)} 个会话:")
    print()
    
    for run_id, session, size in sessions_info:
        print(f"  {run_id}:")
        print(f"    - 开始时间: {session.get('start_time')}")
        print(f"    - 事件数: {session.get('event_count', 0)}")
        print(f"    - 大小: {size / 1024 / 1024:.2f} MB")
        print()
    
    print(f"总计:")
    print(f"  - 会话数: {len(sessions_info)}")
    print(f"  - 总大小: {total_size / 1024 / 1024:.2f} MB")
    print()
    
    print("警告: 这将删除所有会话数据!")
    confirm = input("确认删除所有会话? 输入 'DELETE ALL' 确认: ")
    if confirm != 'DELETE ALL':
        print("取消删除")
        return
    
    print()
    print("开始删除...")
    
    for run_id, _, _ in sessions_info:
        if storage.delete_session(run_id):
            print(f"  已删除: {run_id}")
        else:
            print(f"  删除失败: {run_id}")
    
    print()
    print(f"清理完成!")
    print(f"  - 删除了 {len(sessions_info)} 个会话")
    print(f"  - 释放了 {total_size / 1024 / 1024:.2f} MB 空间")


if __name__ == '__main__':
    try:
        show_menu()
    except KeyboardInterrupt:
        print("\n\n已退出")
        sys.exit(0)
