ANTHROPIC_API_KEY = ""  # Replace with your actual API key or set it as an environment variable

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

if load_dotenv is not None:
    load_dotenv()


@dataclass
class FailureAnalysis:
    test_name: str
    failure_type: str
    root_cause: str
    suggested_fix: str
    confidence: str
    similar_failures: List[str]
    timestamp: str
    full_analysis: str


class AITestAnalyzer:

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or ANTHROPIC_API_KEY
        self.client = None

        if anthropic and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as exc:
                logger.warning(f"Claude client initialization failed: {exc}")
        else:
            logger.warning(
                "Claude API not available. Install 'anthropic' package and set ANTHROPIC_API_KEY. "
                "Run: pip install anthropic"
            )

    def is_available(self) -> bool:
        return self.client is not None

    def analyze_failure(
        self,
        test_name: str,
        error_message: str,
        traceback: str,
        test_code: Optional[str] = None,
        logs: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[FailureAnalysis]:
        if not self.is_available():
            logger.warning("AI analysis not available - skipping")
            return None

        prompt = self._build_analysis_prompt(
            test_name, error_message, traceback, test_code, logs, context
        )

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text
            analysis = self._parse_analysis(test_name, response_text)

            logger.info(f"AI analysis completed for {test_name}")
            return analysis

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None

    def _build_analysis_prompt(
        self,
        test_name: str,
        error_message: str,
        traceback: str,
        test_code: Optional[str],
        logs: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build the prompt for Claude API."""

        prompt = f"""Analyze this test automation failure and provide actionable insights.

TEST NAME: {test_name}

ERROR MESSAGE:
{error_message}

TRACEBACK:
{traceback}
"""

        if test_code:
            prompt += f"\n\nTEST CODE:\n{test_code}\n"

        if logs:
            prompt += f"\n\nRELEVANT LOGS:\n{logs}\n"

        if context:
            prompt += f"\n\nCONTEXT:\n{json.dumps(context, indent=2)}\n"

        prompt += """
Please provide a structured analysis with the following:

1. FAILURE TYPE: Categorize as one of:
   - Assertion Error
   - Timeout/Synchronization
   - Element Not Found
   - Network/API Issue
   - Environment/Setup Issue
   - Data Issue
   - Race Condition
   - Flaky Test
   - Code Bug
   - Other

2. ROOT CAUSE: Brief explanation of what caused the failure (2-3 sentences)

3. SUGGESTED FIX: Specific, actionable steps to fix the issue (3-5 bullet points)

4. CONFIDENCE: High/Medium/Low based on available information

5. SIMILAR PATTERNS: List any common patterns this failure might share with other issues

Format your response as:
FAILURE_TYPE: <type>
ROOT_CAUSE: <cause>
SUGGESTED_FIX:
- <fix 1>
- <fix 2>
- <fix 3>
CONFIDENCE: <level>
SIMILAR_PATTERNS:
- <pattern 1>
- <pattern 2>
"""
        return prompt

    def _parse_analysis(self, test_name: str, response: str) -> FailureAnalysis:
        failure_type = self._extract_section(response, "FAILURE_TYPE")
        root_cause = self._extract_section(response, "ROOT_CAUSE")
        suggested_fix = self._extract_section(response, "SUGGESTED_FIX")
        confidence = self._extract_section(response, "CONFIDENCE")
        similar_patterns = self._extract_list(response, "SIMILAR_PATTERNS")

        return FailureAnalysis(
            test_name=test_name,
            failure_type=failure_type or "Unknown",
            root_cause=root_cause or "Unable to determine",
            suggested_fix=suggested_fix or "No suggestions available",
            confidence=confidence or "Low",
            similar_failures=similar_patterns,
            timestamp=datetime.now().isoformat(),
            full_analysis=response
        )

    @staticmethod
    def _extract_section(text: str, section_name: str) -> Optional[str]:
        flexible_name = section_name.replace('_', r'[\s_]')

        markdown_pattern = rf"##\s+{flexible_name}\s*\n(.*?)(?=\n##\s+|\Z)"
        match = re.search(markdown_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Remove bold
            content = re.sub(r'`(.+?)`', r'\1', content)  # Remove code backticks
            return content

        plain_pattern = rf"{flexible_name}:\s*(.+?)(?=\n[A-Z_]+:|\Z)"
        match = re.search(plain_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    @staticmethod
    def _extract_list(text: str, section_name: str) -> List[str]:
        """Extract a list from the response (handles both plain text and Markdown formats)."""
        flexible_name = section_name.replace('_', r'[\s_]')

        markdown_pattern = rf"##\s+{flexible_name}\s*\n(.*?)(?=\n##\s+|\Z)"
        match = re.search(markdown_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            items = re.findall(r'[-•*]\s*\*?\*?(.+?)(?:\*\*)?$', match.group(1), re.MULTILINE)
            cleaned_items = []
            for item in items:
                item = item.strip()
                item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)  # Remove bold
                item = re.sub(r'`(.+?)`', r'\1', item)  # Remove backticks
                if item:
                    cleaned_items.append(item)
            return cleaned_items

        plain_pattern = rf"{flexible_name}:\s*\n((?:[-•]\s*.+\n?)+)"
        match = re.search(plain_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            items = re.findall(r'[-•]\s*(.+)', match.group(1))
            return [item.strip() for item in items if item.strip()]

        return []

    def analyze_multiple_failures(
        self,
        failures: List[Dict[str, Any]]
    ) -> List[FailureAnalysis]:
        analyses = []

        for failure in failures:
            analysis = self.analyze_failure(
                test_name=failure.get("test_name", "Unknown"),
                error_message=failure.get("error_message", ""),
                traceback=failure.get("traceback", ""),
                test_code=failure.get("test_code"),
                logs=failure.get("logs"),
                context=failure.get("context")
            )

            if analysis:
                analyses.append(analysis)

        return analyses

    def generate_summary_report(
        self,
        analyses: List[FailureAnalysis],
        output_path: Optional[str] = None
    ) -> str:
        report = "=" * 80 + "\n"
        report += "AI-POWERED TEST FAILURE ANALYSIS REPORT\n"
        report += "=" * 80 + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Failures Analyzed: {len(analyses)}\n\n"

        categories: Dict[str, List[FailureAnalysis]] = {}
        for analysis in analyses:
            category = analysis.failure_type
            if category not in categories:
                categories[category] = []
            categories[category].append(analysis)

        report += "FAILURE BREAKDOWN BY TYPE:\n"
        report += "-" * 80 + "\n"
        for category, items in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            report += f"{category}: {len(items)} failures\n"

        report += "\n" + "=" * 80 + "\n"
        report += "DETAILED ANALYSIS\n"
        report += "=" * 80 + "\n\n"

        for i, analysis in enumerate(analyses, 1):
            report += f"\n{i}. {analysis.test_name}\n"
            report += "-" * 80 + "\n"
            report += f"Failure Type: {analysis.failure_type}\n"
            report += f"Confidence: {analysis.confidence}\n\n"
            report += f"Root Cause:\n{analysis.root_cause}\n\n"
            report += f"Suggested Fix:\n{analysis.suggested_fix}\n\n"

            if analysis.similar_failures:
                report += "Similar Patterns:\n"
                for pattern in analysis.similar_failures:
                    report += f"  - {pattern}\n"
                report += "\n"

        if output_path:
            Path(output_path).write_text(report)
            logger.info(f"Report saved to {output_path}")

        return report

    def export_to_json(
        self,
        analyses: List[FailureAnalysis],
        output_path: str
    ) -> None:
        """Export analyses to JSON format."""
        data = [asdict(analysis) for analysis in analyses]

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Analysis exported to {output_path}")


def analyze_test_failure(
    test_name: str,
    error_message: str,
    traceback: str,
    **kwargs
) -> Optional[FailureAnalysis]:
    analyzer = AITestAnalyzer(api_key=ANTHROPIC_API_KEY)
    return analyzer.analyze_failure(test_name, error_message, traceback, **kwargs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = AITestAnalyzer(api_key=ANTHROPIC_API_KEY)

    if not analyzer.is_available():
        print("AI Analyzer not available. Please:")
        print("   1. Install: pip install anthropic")
        print("   2. Set API key: export ANTHROPIC_API_KEY='your-key'")
    else:
        print("AI Test Analyzer is ready!")
        print("\nExample usage:")
        print("="*60)
        print("""
from ai_test_analyzer import analyze_test_failure

analysis = analyze_test_failure(
    test_name="test_user_login",
    error_message="TimeoutException: Element not found",
    traceback="Traceback...",
    test_code="def test_user_login()...",
    logs="Browser logs..."
)

if analysis:
    print(f"Type: {analysis.failure_type}")
    print(f"Root Cause: {analysis.root_cause}")
    print(f"Fix: {analysis.suggested_fix}")
""")
