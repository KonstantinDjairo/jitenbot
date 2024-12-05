from bot.yomichan.exporters.base.monokakido import MonokakidoExporter


class Exporter(MonokakidoExporter):
    def _get_attribution(self, entries):
        return "© Sanseido Co., LTD. 2021"
