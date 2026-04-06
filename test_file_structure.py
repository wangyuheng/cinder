"""
Test file structure generation with LLM.
"""

from cinder_cli.config import Config
from cinder_cli.executor.task_planner import TaskPlanner


def test_file_structure_generation():
    """Test that LLM generates proper file structure with English filenames."""
    config = Config()
    config._config["ollama_debug"] = True
    planner = TaskPlanner(config)
    
    goal = "创建一个python项目，包含输出字符串'hello_world'和执行python代码的功能"
    
    print("\n" + "="*80)
    print("测试目标:", goal)
    print("="*80)
    
    result = planner.decompose_goal_with_validation(
        goal,
        constraints=None,
        max_retries=1,
        quality_threshold=0.7,
    )
    
    print("\n生成的任务:")
    for i, task in enumerate(result.get("subtasks", []), 1):
        print(f"\n任务 {i}:")
        print(f"  文件路径: {task.get('file_path')}")
        print(f"  描述: {task.get('description')}")
        print(f"  语言: {task.get('language')}")
        print(f"  类型: {task.get('type')}")
        print(f"  功能: {task.get('features', [])}")
    
    print("\n" + "="*80)
    print("验证文件名:")
    print("="*80)
    
    all_valid = True
    for task in result.get("subtasks", []):
        file_path = task.get("file_path", "")
        
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in file_path)
        has_special = any(char in file_path for char in ["'", '"', " ", "(", ")", "（", "）"])
        
        if has_chinese:
            print(f"❌ {file_path} - 包含中文字符")
            all_valid = False
        elif has_special:
            print(f"❌ {file_path} - 包含特殊字符")
            all_valid = False
        else:
            print(f"✅ {file_path} - 文件名符合规范")
    
    print("\n" + "="*80)
    if all_valid:
        print("✅ 所有文件名都符合规范！")
    else:
        print("❌ 存在不符合规范的文件名")
    print("="*80)
    
    return result


if __name__ == "__main__":
    test_file_structure_generation()
