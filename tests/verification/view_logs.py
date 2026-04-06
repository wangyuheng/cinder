#!/usr/bin/env python3
"""查看 Cinder CLI 执行日志的示例脚本"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def view_execution_logs():
    """查看执行日志"""
    db_path = Path.home() / ".cinder" / "executions.db"
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT id, timestamp, goal, status, created_files, execution_time
            FROM executions 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        print("\n" + "="*80)
        print("📊 最近的执行记录")
        print("="*80)
        
        for row in cursor.fetchall():
            print(f"\n执行 ID: {row['id']}")
            print(f"时间: {row['timestamp']}")
            print(f"目标: {row['goal']}")
            print(f"状态: {row['status']}")
            
            created_files = json.loads(row['created_files']) if row['created_files'] else []
            if created_files:
                print(f"创建的文件: {', '.join(created_files)}")
            
            if row['execution_time']:
                print(f"执行时间: {row['execution_time']:.2f}秒")

def view_decision_logs():
    """查看决策日志"""
    db_path = Path.home() / ".cinder" / "decisions.db"
    
    if not db_path.exists():
        print("❌ 决策数据库文件不存在")
        return
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT id, timestamp, confidence, requires_human, reviewed
            FROM decisions 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        print("\n" + "="*80)
        print("🤖 最近的决策记录")
        print("="*80)
        
        for row in cursor.fetchall():
            print(f"\n决策 ID: {row['id']}")
            print(f"时间: {row['timestamp']}")
            print(f"置信度: {row['confidence']:.2f}")
            print(f"需要人工干预: {'是' if row['requires_human'] else '否'}")
            print(f"已审核: {'是' if row['reviewed'] else '否'}")

def view_execution_detail(execution_id: int):
    """查看特定执行的详细信息"""
    db_path = Path.home() / ".cinder" / "executions.db"
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM executions WHERE id = ?
        """, (execution_id,))
        
        row = cursor.fetchone()
        if not row:
            print(f"❌ 执行 ID {execution_id} 不存在")
            return
        
        print("\n" + "="*80)
        print(f"📋 执行详情 #{execution_id}")
        print("="*80)
        print(f"\n目标: {row['goal']}")
        print(f"状态: {row['status']}")
        print(f"时间: {row['timestamp']}")
        
        if row['task_tree']:
            task_tree = json.loads(row['task_tree'])
            print(f"\n任务树:")
            for i, task in enumerate(task_tree.get('subtasks', []), 1):
                print(f"  {i}. {task.get('description', 'N/A')}")
        
        if row['results']:
            results = json.loads(row['results'])
            print(f"\n执行结果:")
            for i, result in enumerate(results, 1):
                if 'file_result' in result:
                    print(f"  文件 {i}: {result['file_result'].get('file_path')}")

if __name__ == "__main__":
    print("\n🔍 Cinder CLI 日志查看器\n")
    
    view_execution_logs()
    view_decision_logs()
    
    print("\n" + "="*80)
    print("💡 提示:")
    print("  - 使用 'python -m cinder_cli execution list' 查看执行列表")
    print("  - 使用 'python -m cinder_cli execution show <id>' 查看详情")
    print("  - 使用 'python -m cinder_cli decisions list' 查看决策列表")
    print("  - 数据库位置: ~/.cinder/executions.db 和 ~/.cinder/decisions.db")
    print("="*80 + "\n")
