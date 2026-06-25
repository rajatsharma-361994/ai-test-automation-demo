import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from ai_test_analyzer import AITestAnalyzer, FailureAnalysis


class AIAnalyzerPlugin:

    def __init__(self, config):
        self.config = config
        self.analyzer = AITestAnalyzer()
        self.failures: List[Dict[str, Any]] = []
        self.analyses: List[FailureAnalysis] = []
        self.enabled = config.getoption("--ai-analyze", default=False)

        print("\n" + "=" * 80)
        print("AI ANALYZER PLUGIN INITIALIZED")
        print("=" * 80)
        print(f"Enabled: {self.enabled}")
        print(f"Analyzer Available: {self.analyzer.is_available()}")

        if self.enabled and not self.analyzer.is_available():
            print("AI analysis enabled but not available. Install 'anthropic' package and set ANTHROPIC_API_KEY")
            self.enabled = False

        if self.enabled:
            print("AI Analyzer is READY and will analyze failures")
        else:
            print("AI Analyzer is DISABLED")
        print("=" * 80)

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()

        if report.when == "call" and report.failed and self.enabled:
            self._capture_failure(item, report)

    def _capture_failure(self, item, report):
        """Capture failure information for analysis."""
        failure_info = {
            "test_name": item.nodeid,
            "error_message": str(report.longrepr),
            "traceback": self._get_traceback(report),
            "test_code": self._get_test_code(item),
            "context": {
                "file": str(item.fspath),
                "line": item.location[1],
                "duration": report.duration,
                "markers": [marker.name for marker in item.iter_markers()],
            },
        }

        self.failures.append(failure_info)
        print(f"[AI ANALYZER] Captured failure: {item.nodeid}")

    @staticmethod
    def _get_traceback(report) -> str:
        """Extract traceback from report."""
        if hasattr(report.longrepr, "reprtraceback"):
            return str(report.longrepr.reprtraceback)
        return str(report.longrepr)

    @staticmethod
    def _get_test_code(item) -> Optional[str]:
        """Extract test source code."""
        try:
            return inspect.getsource(item.function)
        except Exception:
            return None

    def pytest_sessionfinish(self, session, exitstatus):
        """Hook called after all tests complete."""
        if not self.enabled:
            print("[AI ANALYZER] Skipping - plugin not enabled")
            return

        if not self.failures:
            print("[AI ANALYZER] Skipping - no failures captured")
            return

        print(f"[AI ANALYZER] Analyzing {len(self.failures)} failures with AI...")

        for failure in self.failures:
            analysis = self.analyzer.analyze_failure(
                test_name=failure["test_name"],
                error_message=failure["error_message"],
                traceback=failure["traceback"],
                test_code=failure.get("test_code"),
                context=failure.get("context"),
            )

            if analysis:
                self.analyses.append(analysis)
                print(f"[AI ANALYZER] ✓ Analysis complete for {failure['test_name']}")
            else:
                print(f"[AI ANALYZER] ✗ Analysis failed for {failure['test_name']}")

        if self.analyses:
            self._generate_reports()
        else:
            print("[AI ANALYZER] No analyses to report")

    def _generate_reports(self):
        """Generate analysis reports."""
        output_dir = Path(self.config.getoption("--ai-report-dir", default="ai-analysis"))
        output_dir.mkdir(exist_ok=True)
        print(f"[AI ANALYZER] Report directory: {output_dir.absolute()}")

        txt_report_path = output_dir / "ai_failure_analysis.txt"
        self.analyzer.generate_summary_report(self.analyses, str(txt_report_path))
        print(f"[AI ANALYZER] ✓ Text report saved: {txt_report_path}")

        json_report_path = output_dir / "ai_failure_analysis.json"
        self.analyzer.export_to_json(self.analyses, str(json_report_path))
        print(f"[AI ANALYZER] ✓ JSON report saved: {json_report_path}")

        self._print_console_summary()

    def _print_console_summary(self):
        print("\n" + "=" * 80)
        print("AI FAILURE ANALYSIS SUMMARY")
        print("=" * 80)

        categories: Dict[str, List[FailureAnalysis]] = {}
        for analysis in self.analyses:
            category = analysis.failure_type
            if category not in categories:
                categories[category] = []
            categories[category].append(analysis)

        print(f"\nAnalyzed {len(self.analyses)} failures:")
        for category, items in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  • {category}: {len(items)}")

        high_confidence = [a for a in self.analyses if a.confidence == "High"]
        if high_confidence:
            print(f"\n{len(high_confidence)} high-confidence analyses:")
            for analysis in high_confidence[:3]:
                print(f"\n  {analysis.test_name}")
                print(f"  Root Cause: {analysis.root_cause[:100]}...")
                print(f"  Fix: {analysis.suggested_fix[:100]}...")

        print("\n" + "=" * 80)
        print("Full reports available in ai-analysis/ directory")
        print("=" * 80)


def analyze_failure_report(item, excinfo, call=None):
    analyzer = AITestAnalyzer()
    if not analyzer.is_available():
        print("AI Analyzer not available. Please install the anthropic package and set ANTHROPIC_API_KEY.")
        return None

    test_name = getattr(item, "nodeid", item.name)
    error_message = str(excinfo.value)
    traceback = ""

    if excinfo.tb is not None:
        traceback = "\n".join(pytest._code.ExceptionInfo.from_exc_info(excinfo).traceback)

    analysis = analyzer.analyze_failure(
        test_name=test_name,
        error_message=error_message,
        traceback=traceback,
        test_code=None,
        logs=None,
        context={"pytest_nodeid": test_name},
    )

    if analysis is None:
        print("AI analysis could not be generated.")
        return None

    print("\nAI Analysis")
    print("=" * 60)
    print(f"Failure Type: {analysis.failure_type}")
    print(f"Confidence: {analysis.confidence}")
    print(f"Root Cause: {analysis.root_cause}")
    print("Suggested Fix:")
    print(analysis.suggested_fix)
    if analysis.similar_failures:
        print("Similar Patterns:")
        for pattern in analysis.similar_failures:
            print(f"- {pattern}")

    return analysis


def pytest_addoption(parser):
    """Add command-line options for AI analysis."""
    group = parser.getgroup("ai-analyzer")

    group.addoption(
        "--ai-analyze",
        action="store_true",
        default=False,
        help="Enable AI-powered failure analysis using Claude API",
    )

    group.addoption(
        "--ai-report-dir",
        action="store",
        default="ai-analysis",
        help="Directory to save AI analysis reports (default: ai-analysis)",
    )


def pytest_configure(config):
    """Register the plugin."""
    if config.getoption("--ai-analyze"):
        config.pluginmanager.register(AIAnalyzerPlugin(config), "ai_analyzer")


@pytest.fixture
def ai_analyzer():
    return AITestAnalyzer()
