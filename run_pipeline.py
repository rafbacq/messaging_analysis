import os
import argparse
import logging
from src.parser.factory import get_parser
from src.processing.cleaner import DataCleaner
from src.processing.sessionizer import Sessionizer
from src.features.stats import StatsExtractor
from src.features.nlp import NLPProcessor
from src.features.dynamics import DynamicsScorer
from src.modeling.engagement import EngagementModel
from src.reporting.generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Messaging Analysis Pipeline")
    parser.add_argument("--input", type=str, default="text_data", help="Input directory")
    parser.add_argument("--output", type=str, default="outputs", help="Output directory")
    parser.add_argument("--my-name", type=str, default="Me", help="Your name for sender normalization")
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_messages = []
    
    # 1. Ingestion
    logger.info(f"Scanning {input_dir} for HTML files...")
    if not os.path.exists(input_dir):
        logger.error(f"Input directory {input_dir} not found.")
        return
        
    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(input_dir, filename)
            logger.info(f"Parsing {file_path}...")
            try:
                parser_obj = get_parser(file_path, my_name=args.my_name)
                msgs = parser_obj.parse()
                all_messages.extend(msgs)
                logger.info(f"Extracted {len(msgs)} messages from {filename}")
            except Exception as e:
                logger.error(f"Failed to parse {filename}: {e}")

    if not all_messages:
        logger.warning("No messages parsed. Exiting.")
        return

    # 2. Processing
    logger.info("Cleaning and sorting messages...")
    cleaner = DataCleaner()
    all_messages = cleaner.clean_messages(all_messages)
    
    logger.info("Sessionizing messages...")
    sessionizer = Sessionizer()
    sessions = sessionizer.group_into_sessions(all_messages)
    logger.info(f"Created {len(sessions)} sessions.")

    # 3. Features
    logger.info("Extracting features...")
    stats_ext = StatsExtractor()
    overall_stats = stats_ext.compute_overall_stats(all_messages)
    person_stats = stats_ext.compute_person_stats(all_messages)
    
    nlp_proc = NLPProcessor()
    nlp_features = nlp_proc.process_messages(all_messages)
    nlp_feat_dict = {f["message_id"]: f for f in nlp_features}
    
    dynamics = DynamicsScorer()
    session_scores = [dynamics.compute_session_scores(s, nlp_feat_dict) for s in sessions]

    # 4. Modeling
    logger.info("Training models...")
    model = EngagementModel()
    model_results = model.train(sessions)

    # 5. Reporting
    logger.info("Generating report...")
    reporter = ReportGenerator(output_dir)
    report_path = reporter.generate(overall_stats, person_stats, model_results)
    
    logger.info(f"Pipeline complete! Report saved to {report_path}")

if __name__ == "__main__":
    main()
