import unittest

from screaper.engine.markup_processor import LinkProcessor


class TestMarkupProcessor(unittest.TestCase):

    link_processor = LinkProcessor()

    def test_link_processor(self):

        test1 = "https://www.google.com/"
        target_url, _, _ = self.link_processor.process(test1, referrer_url="")
        assert target_url == "www.google.com/", target_url

        test2 = "google.com/"
        target_url, _, _ = self.link_processor.process(test2, referrer_url="")
        assert target_url == "google.com/", target_url

        test3 = "google.com/#anchor"
        target_url, _, _ = self.link_processor.process(test3, referrer_url="")
        assert target_url == "google.com/", target_url

        test4 = "/relative-path"
        target_url, _, _ = self.link_processor.process(test4, referrer_url="google.com/")
        assert target_url == "google.com/relative-path", target_url

        test5 = "/"
        target_url, _, _ = self.link_processor.process(test5, referrer_url="google.com/")
        assert target_url == "google.com/", target_url

        test6 = "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide"
        target_url, _, _ = self.link_processor.process(test6, referrer_url="google.com/")
        assert target_url == "www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide", target_url

        test7 = "https://www.europages.de/Maschinenbau%20und%20Industrie%20-%20Ausr%C3%BCstungen.html"
        target_url, _, _ = self.link_processor.process(test7, referrer_url="google.com/")
        assert target_url == "www.europages.de/Maschinenbau%20und%20Industrie%20-%20Ausr%C3%BCstungen.html", target_url

if __name__ == "__main__":
    print("Check what URL returns")
    test = TestMarkupProcessor()
    test.test_link_processor()

