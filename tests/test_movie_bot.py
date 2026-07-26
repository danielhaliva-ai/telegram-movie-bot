import unittest
from unittest.mock import patch

from movie_bot import build_movie_results_message, handle_message


class BuildMovieResultsMessageTest(unittest.TestCase):
    def test_build_message_with_no_results(self):
        self.assertEqual(
            build_movie_results_message("inception", []),
            "לא נמצאו תוצאות עבור: inception",
        )

    def test_build_message_with_results(self):
        movies = [
            {"trackName": "Inception", "releaseDate": "2010-07-08T07:00:00Z"},
            {"trackName": "Interstellar"},
        ]
        self.assertEqual(
            build_movie_results_message("nolan", movies),
            "תוצאות עבור: nolan\n- Inception (2010)\n- Interstellar",
        )


class HandleMessageTest(unittest.TestCase):
    @patch("movie_bot.telegram_api_request")
    @patch("movie_bot.search_movies")
    def test_movie_command_searches_and_sends(self, mock_search_movies, mock_telegram):
        mock_search_movies.return_value = [{"trackName": "Inception", "releaseDate": "2010"}]

        handle_message("token", 123, "/movie inception")

        mock_search_movies.assert_called_once_with("inception")
        mock_telegram.assert_called_once()


if __name__ == "__main__":
    unittest.main()
