DOCSTRING_ALL_RETURN_SINGLE = [
    {
        "mk_file_path": "file1.md",
        "code_file": "function_1.py",
        "code_file_path": "/path/to/function_1.py",
        "hazards": [
            {
                "sub_routine": "sub_routine_1",
                "hazard_full": "WrongPatient (1): The wrong patient",
                "hazard_number": "1",
            }
        ],
    },
    {
        "mk_file_path": "file2.md",
        "code_file": "function_2.py",
        "code_file_path": "/path/to/function_2.py",
        "hazards": [
            {
                "sub_routine": "sub_routine_2",
                "hazard_full": "WrongDemograhics (2): The wrong patient gender",
                "hazard_number": "2",
            }
        ],
    },
]

DOCSTRING_ALL_RETURN_DOUBLE = [
    {
        "mk_file_path": "file1.md",
        "code_file": "function_1.py",
        "code_file_path": "/path/to/function_1.py",
        "hazards": [
            {
                "sub_routine": "sub_routine_1",
                "hazard_full": "WrongPatient (1): The wrong patient",
                "hazard_number": "1",
            }
        ],
    },
    {
        "mk_file_path": "file2.md",
        "code_file": "function_2.py",
        "code_file_path": "/path/to/function_2.py",
        "hazards": [
            {
                "sub_routine": "sub_routine_2",
                "hazard_full": "WrongDemograhics (2): The wrong patient gender",
                "hazard_number": "2",
            }
        ],
    },
    {
        "mk_file_path": "file2.md",
        "code_file": "function_3.py",
        "code_file_path": "/path/to/function_3.py",
        "hazards": [
            {
                "sub_routine": "sub_routine_3",
                "hazard_full": "WrongDemograhics (3): The wrong patient address",
                "hazard_number": "3",
            }
        ],
    },
]

PROVIDED_DOCSTRING = (
    "def a_test_function(a_string, a_number) -> bool:\n"
    '   """A test Docstring\n'
    "\n"
    "   Testing the extraction of docstrings\n"
    "\n"
    "   Args:\n"
    "       a_string (str): This is a string.\n"
    "       a_number (int): This is a number.\n"
    "\n"
    "   Returns:\n"
    "       bool: True if successful.\n"
    "\n"
    "   Hazards:\n"
    "       WrongPatient (1): The wrong patient\n"
    "       WrongDemographics (2): The wrong gender\n"
    '   """\n'
    "   print(a_string)\n"
    "   print(a_number)\n"
    "   return True\n"
)

RETURN_DOCSTRING = [
    (
        "a_test_function",
        "A test Docstring\n\n   Testing the extraction of docstrings\n\n   Args:\n       a_string (str): This is a string.\n       a_number (int): This is a number.\n\n   Returns:\n       bool: True if successful.\n\n   Hazards:\n       WrongPatient (1): The wrong patient\n       WrongDemographics (2): The wrong gender\n   ",
    )
]

DOCSTRING_NON_DIGIT_HAZARD_NUMBER = [
    (
        "a_test_function",
        "A test Docstring\n\n   Testing the extraction of docstrings\n\n   Args:\n       a_string (str): This is a string.\n       a_number (int): This is a number.\n\n   Returns:\n       bool: True if successful.\n\n   Hazards:\n       WrongPatient (a): The wrong patient\n       WrongDemographics (b): The wrong gender\n   ",
    )
]


RETURN_DOCSTRING_NO_HAZARDS = [
    (
        "a_test_function",
        "A test Docstring\n\n   Testing the extraction of docstrings\n\n   Args:\n       a_string (str): This is a string.\n       a_number (int): This is a number.\n\n   Returns:\n       bool: True if successful.\n",
    )
]

RETURN_HAZARDS = [
    {
        "sub_routine": "a_test_function",
        "hazard_full": "WrongPatient (1): The wrong patient",
        "hazard_number": "1",
    },
    {
        "sub_routine": "a_test_function",
        "hazard_full": "WrongDemographics (2): The wrong gender",
        "hazard_number": "2",
    },
]

RETURN_HAZARDS_NON_DIGIT_HAZARD_NUMBER = [
    {
        "sub_routine": "a_test_function",
        "hazard_full": "WrongPatient (a): The wrong patient",
        "hazard_number": None,
    },
    {
        "sub_routine": "a_test_function",
        "hazard_full": "WrongDemographics (b): The wrong gender",
        "hazard_number": None,
    },
]
