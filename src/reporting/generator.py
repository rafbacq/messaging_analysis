import os
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, stats: Dict[str, Any], person_stats: Dict[str, Any], model_results: Dict[str, Any]):
        report_path = os.path.join(self.output_dir, "report.md")
        
        lines = [
            "# Messaging Analysis Report",
            "",
            "## Privacy Notice",
            "This report is generated locally. No private message data has been uploaded. "
            "Interpretations of emotions or relationship quality are probabilistic estimates based on observable behavioral patterns and should not be taken as absolute truth.",
            "",
            "## Executive Summary",
            f"- **Total Messages**: {stats.get('total_messages', 0)}",
            f"- **Active Days**: {stats.get('active_days', 0)}",
            f"- **Total Words**: {stats.get('total_words', 0)}",
            "",
            "## Per-Person Statistics"
        ]
        
        for person, p_stats in person_stats.items():
            lines.append(f"### {person}")
            lines.append(f"- Messages: {p_stats.get('message_count', 0)}")
            lines.append(f"- Words: {p_stats.get('word_count', 0)}")
            lines.append(f"- Avg Message Length: {p_stats.get('avg_message_length', 0):.1f} words")
            lines.append("")
            
        lines.extend([
            "## Model Evaluation",
            "### Engagement Prediction",
            f"- Accuracy: {model_results.get('accuracy', 0.0):.2f}"
        ])
        
        if 'feature_importances' in model_results:
            lines.append("- Top Features:")
            for feat, imp in model_results['feature_importances'][:3]:
                lines.append(f"  - {feat}: {imp:.4f}")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        return report_path
