import unittest


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover('./shared_utils/tests')
    runner = unittest.TextTestRunner()
    runner.run(suite)
