def parameterized_test(*test_cases):
    def decorator(test_func):
        def wrapper(self):
            for case in test_cases:
                with self.subTest(case=case):
                    test_func(self, *case)
        return wrapper
    return decorator
