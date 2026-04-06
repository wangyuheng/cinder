#!/usr/bin/env python3
"""
Code coverage analysis script for progress tracking enhancement.

This script runs pytest with coverage analysis and generates a detailed report.
Target: > 80% code coverage for progress tracking modules.
"""

import subprocess
import sys
from pathlib import Path


def run_coverage_analysis():
    """Run pytest with coverage analysis."""
    print("=" * 80)
    print("Code Coverage Analysis for Progress Tracking Enhancement")
    print("=" * 80)
    print()
    
    coverage_cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=cinder_cli.executor.progress_tracker",
        "--cov=cinder_cli.executor.progress_broadcaster",
        "--cov=cinder_cli.executor.time_recorder",
        "--cov=cinder_cli.executor.speed_calculator",
        "--cov=cinder_cli.executor.estimation_engine",
        "--cov=cinder_cli.executor.execution_logger",
        "--cov=cinder_cli.web.api.progress",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_report",
        "--cov-report=xml:coverage.xml",
        "--tb=short",
    ]
    
    print("Running command:")
    print(" ".join(coverage_cmd))
    print()
    
    result = subprocess.run(coverage_cmd, cwd=Path(__file__).parent.parent)
    
    print()
    print("=" * 80)
    print("Coverage Analysis Complete")
    print("=" * 80)
    print()
    print("Reports generated:")
    print("  - Terminal output above")
    print("  - HTML report: coverage_report/index.html")
    print("  - XML report: coverage.xml")
    print()
    
    if result.returncode == 0:
        print("✓ All tests passed")
    else:
        print("✗ Some tests failed")
    
    return result.returncode


def check_coverage_threshold():
    """Check if coverage meets the 80% threshold."""
    import xml.etree.ElementTree as ET
    
    coverage_file = Path(__file__).parent.parent / "coverage.xml"
    
    if not coverage_file.exists():
        print("Coverage report not found. Run coverage analysis first.")
        return False
    
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    line_rate = float(root.attrib.get("line-rate", 0))
    coverage_percentage = line_rate * 100
    
    print()
    print("=" * 80)
    print(f"Overall Coverage: {coverage_percentage:.2f}%")
    print("=" * 80)
    
    if coverage_percentage >= 80.0:
        print("✓ Coverage meets the 80% threshold")
        return True
    else:
        print(f"✗ Coverage below 80% threshold (current: {coverage_percentage:.2f}%)")
        return False


def generate_module_coverage_report():
    """Generate detailed coverage report for each module."""
    import xml.etree.ElementTree as ET
    
    coverage_file = Path(__file__).parent.parent / "coverage.xml"
    
    if not coverage_file.exists():
        print("Coverage report not found. Run coverage analysis first.")
        return
    
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    print()
    print("=" * 80)
    print("Module Coverage Breakdown")
    print("=" * 80)
    print()
    
    modules = []
    for package in root.findall(".//package"):
        name = package.attrib.get("name", "")
        line_rate = float(package.attrib.get("line-rate", 0))
        coverage = line_rate * 100
        
        if "progress" in name or "estimation" in name:
            modules.append((name, coverage))
    
    modules.sort(key=lambda x: x[1], reverse=True)
    
    for name, coverage in modules:
        status = "✓" if coverage >= 80.0 else "✗"
        print(f"{status} {name:50s} {coverage:6.2f}%")
    
    print()
    
    avg_coverage = sum(c for _, c in modules) / len(modules) if modules else 0
    print(f"Average Coverage: {avg_coverage:.2f}%")
    print()


def main():
    """Main entry point."""
    print()
    print("Starting code coverage analysis...")
    print()
    
    returncode = run_coverage_analysis()
    
    if returncode == 0:
        check_coverage_threshold()
        generate_module_coverage_report()
    
    return returncode


if __name__ == "__main__":
    sys.exit(main())
