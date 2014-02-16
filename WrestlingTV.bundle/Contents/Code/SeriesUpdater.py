import ImageUpdater
import SeasonUpdater
import TVRageNetwork
import WrestlingConstants


class Updater:
    def __init__(self, metadata, media, lang):
        self.tvrage_id = metadata.id
        self.metadata = metadata
        self.media = media

    def update(self):
        Log("update %s: START" % self.tvrage_id)
        xml = TVRageNetwork.fetchXML(TVRageNetwork.TVRAGE_SHOW_INFO_URL % self.tvrage_id)

        self.metadata.title = xml.xpath("/Showinfo/showname")[0].text
        if xml.xpath("/Showinfo/network"):
            self.metadata.studio = xml.xpath("/Showinfo/network")[0].text
        self.metadata.duration = int(xml.xpath("/Showinfo/runtime")[0].text) * 60 * 1000
        self.metadata.originally_available_at = Datetime.ParseDate(xml.xpath("/Showinfo/started")[0].text).date()
        self.metadata.genres = [genre.text for genre in xml.xpath("/Showinfo/genres/genre")]
        if xml.xpath("/Showinfo/summary"):
            self.metadata.summary = xml.xpath("/Showinfo/summary")[0].text
        self.metadata.countries = [xml.xpath("/Showinfo/origin_country")[0].text]
        self.metadata.tags = [xml.xpath("/Showinfo/classification")[0].text]

        self.update_seasons(self.metadata, self.media)
        self.update_images(self.metadata, self.media, xml)
        Log("update: END")

    def update_seasons(self, metadata, media):
        season_updater = SeasonUpdater.Updater(metadata, media.seasons)
        season_updater.update()

    def update_images(self, metadata, media, series_xml):
        tvdb_id = WrestlingConstants.convert_tvrage_to_tvdb(metadata.id)

        if series_xml.xpath("/Showinfo/image") and series_xml.xpath("/Showinfo/image")[0].text != None:
            fallback_image_url = series_xml.xpath("/Showinfo/image")[0].text
        else:
            fallback_image_url = None

        image_updater = ImageUpdater.Updater(metadata, tvdb_id, media.seasons, fallback_image_url)
        image_updater.update()