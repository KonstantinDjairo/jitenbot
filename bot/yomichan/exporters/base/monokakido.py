from datetime import datetime
from bot.yomichan.exporters.base.exporter import BaseExporter


class MonokakidoExporter(BaseExporter):
    def _get_revision(self, entries):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return f"{self._target.value};{timestamp}"
