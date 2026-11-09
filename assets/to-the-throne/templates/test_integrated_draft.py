#!/usr/bin/env python3
"""End-to-end draft integration smoke test using synthetic, unpublishable data."""
import json,tempfile
from pathlib import Path
from integrated_draft import produce
ROOT=Path(__file__).resolve().parent
def main():
    week=json.loads((ROOT/"samples/canonical-demo.json").read_text())
    with tempfile.TemporaryDirectory() as folder:
        status=produce(week,Path(folder)/"package",{})
        assert not status["ready_for_publication"] and status["publication"] is False
        assert status["edition"]==week["edition"]
        assert status["pdfs"]["recording_brief"]["passed"]
        assert status["pdfs"]["public_source_sheet"]["pages"]==6
        assert (Path(folder)/"package/graphics/monday-DRAFT.png").is_file()
        assert "wednesday" in status["missing_components"] and "praise" in status["missing_components"]
        print(json.dumps({"passed":True,"edition":week["edition"],"pdf_pages":[status["pdfs"]["recording_brief"]["pages"],6],
          "monday_draft":True,"missing_updates_flagged":True,"publishing_blocked":True},indent=2))
if __name__=="__main__":main()
