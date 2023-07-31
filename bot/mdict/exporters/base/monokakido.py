from datetime import datetime
from bot.mdict.exporters.base.exporter import BaseExporter


class MonokakidoExporter(BaseExporter):
    def _get_revision(self, entries):
        timestamp = datetime.now().strftime("%Y年%m月%d日作成")
        return timestamp
