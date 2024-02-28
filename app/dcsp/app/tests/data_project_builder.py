from ..models import ViewAccess

REPO_INPUTS_1 = {
    "setup_choice": "import",
    "external_repository_username_import": "username",
    "external_repository_password_token_import": "password",
    "external_repository_url_import": "url",
}

REPO_INPUTS_2 = {
    "repository_type": "github",
    "project_name": "A project name",
    "description": "A description",
    "access": ViewAccess.PUBLIC,
    "members": [1],
    "groups": [1],
}

PLACEHOLDERS_EMPTY = {
    "placeholder1": "",
    "placeholder2": "",
    "placeholder3": "",
    "placeholder4": "",
    "placeholder5": "",
    "placeholder6": "",
}

GET_PLACEHOLDERS_STORED = {
    "placeholder1": "value1",
    "placeholder2": "value2",
    "placeholder3": "value3",
    "placeholder4": "value4",
    "placeholder5": "value5",
    "placeholder6": "value6",
}

TEMPLATE_CONTENTS = """<!-- [icon] -->

### Hazard name
A short name

### General utility label
[multiselect]
1 - Hazard: A hazard which is logged
2 - New hazard for triage: A new hazard which needs to be triaged for severity and likelihood, scored and assigned
3 - Deprecated hazard: A hazard which is no longer considered relevant

### Likelihood scoring
[select] [L]
1 - Very low: Negligible or nearly negligible possibility of occurring
2 - Low: Could occur but in the great majority of occasions will not
3 - Medium: Possible
4 - High: Not certain but very possible; reasonably expected to occur in the majority of cases
5 - Very high: Certain or almost certain; highly likely to occur
    
### Severity scoring
[select] [S]
1 - Minor: Minor injury, short term recovery; minor psychological upset; inconvenience; negligible consequence
2 - Significant: Minor injury, long term, 1; Significant psych. trauma, 1; Minor inj/psych trauma, 2+
3 - Considerable: Severe injury, 1, severe incapacity, recovery expected; Significant psych. trauma, 2+
4 - Major: Death, 1; Severe injury or life-changing incapacity, 1; Psychological trauma, 2+
5 - Catastrophic: Death, 2+. Severe injury or lifechanging incapacity, 2+

### Risk scoring
[calculate] [L] [S]
1 - Acceptable: Acceptable, no further action required [L1-S1, L1-S2, L2-S1]
2 - Acceptable: Acceptable if cost of further reduction > benefits, or further risk reduction is impractical [L1-S3, L1-S4, L2-S2, L2-S3, L3-S1, L3-S2, L4-S1]
3 - Undesirable: Undesirable level of risk. Attempts should be made to eliminate the hazard or implement controls [L1-S5, L2-S4, L3-S3, L3-S4, L4-S2, L4-S3, L5-S1]
4 - Mandatory-risk-elimination: Mandatory elimination of hazard or addition of controls to reduce risk to an acceptable level [L2-S5, L3-S5, L4-S4, L5-S2, L5-S3]
5 - Unacceptable: Unacceptable level of risk [L4-S5, L5-S4, L5-S5]

### Description
A general description of the Hazard. Keep it short. Detail goes below.

### Cause(s)
The upstream system Cause (can be multiple - use a numbered list) that results in the change to intended care.

### Effect
The change in the intended care pathway resulting from the Cause.

### Hazard
The potential for Harm to occur, even if it does not.

### Harm
An actual occurrence of a Hazard in the patient or clinical context. This is what we are assessing the Severity and Likelihood of. This is form normal working conditions and fault conditions. Include the ultimate Risk rating as well.

### Existing controls
List any pre-existing controls that can mitigate the hazard.

-----

### Assignment
Assign this Hazard to its Owner. Default owner is the Clinical Safety Officer

### Labelling
Add labels according to Severity. Likelihood and Risk Level

### Project
Add to the Project 'Clinical Risk Management'

Subsequent discussion can be used to mitigate the Hazard, reducing the likelihood (or less commonly reducing the severity) of the Harm.

If Harm is reduced then you can change the labels to reflect this and reclassify the Risk Score.

Issues can be linked to: Issues describing specific software changes, Pull Requests or Commits fixing Issues, external links, and much more supporting documentation. Aim for a comprehensive, well-evidenced, public and open discussion on risk and safety.

-----

### New hazard controls
List controls that will be put into place to mitigate the hazard. These can include design, (unit/integration) testing, training or business process change.

### Residual hazard risk assessment
Include a repeat analysis of Severity and Likelihood. Include the ultimate Risk rating as well.

### Hazard status
Either 'open', 'transferred' or 'closed'.

### Code associated with hazard
[code]

"""

TEMPLATE_LIST = [
    {"field_type": "icon", "heading": "icon"},
    {
        "field_type": "text_area",
        "heading": "### Hazard name",
        "gui_label": "Hazard name",
        "text": "A short name",
        "number": [],
    },
    {
        "field_type": "multiselect",
        "heading": "### General utility label",
        "gui_label": "General utility label",
        "text": "1 - Hazard: A hazard which is logged\n2 - New hazard for triage: A new hazard which needs to be triaged for severity and likelihood, scored and assigned\n3 - Deprecated hazard: A hazard which is no longer considered relevant",
        "labels": [],
        "choices": (
            ["1 - Hazard: A hazard which is logged", "1 - Hazard"],
            [
                "2 - New hazard for triage: A new hazard which needs to be triaged for severity and likelihood, scored and assigned",
                "2 - New hazard for triage",
            ],
            [
                "3 - Deprecated hazard: A hazard which is no longer considered relevant",
                "3 - Deprecated hazard",
            ],
        ),
        "number": ["1", "2", "3"],
    },
    {
        "field_type": "select",
        "heading": "### Likelihood scoring",
        "gui_label": "Likelihood scoring",
        "text": "1 - Very low: Negligible or nearly negligible possibility of occurring\n2 - Low: Could occur but in the great majority of occasions will not\n3 - Medium: Possible\n4 - High: Not certain but very possible; reasonably expected to occur in the majority of cases\n5 - Very high: Certain or almost certain; highly likely to occur",
        "labels": ["L"],
        "choices": (
            ("", ""),
            [
                "1 - Very low: Negligible or nearly negligible possibility of occurring",
                "1 - Very low",
            ],
            [
                "2 - Low: Could occur but in the great majority of occasions will not",
                "2 - Low",
            ],
            ["3 - Medium: Possible", "3 - Medium"],
            [
                "4 - High: Not certain but very possible; reasonably expected to occur in the majority of cases",
                "4 - High",
            ],
            [
                "5 - Very high: Certain or almost certain; highly likely to occur",
                "5 - Very high",
            ],
        ),
        "number": ["1", "2", "3", "4", "5"],
    },
    {
        "field_type": "select",
        "heading": "### Severity scoring",
        "gui_label": "Severity scoring",
        "text": "1 - Minor: Minor injury, short term recovery; minor psychological upset; inconvenience; negligible consequence\n2 - Significant: Minor injury, long term, 1; Significant psych. trauma, 1; Minor inj/psych trauma, 2+\n3 - Considerable: Severe injury, 1, severe incapacity, recovery expected; Significant psych. trauma, 2+\n4 - Major: Death, 1; Severe injury or life-changing incapacity, 1; Psychological trauma, 2+\n5 - Catastrophic: Death, 2+. Severe injury or lifechanging incapacity, 2+",
        "labels": ["S"],
        "choices": (
            ("", ""),
            [
                "1 - Minor: Minor injury, short term recovery; minor psychological upset; inconvenience; negligible consequence",
                "1 - Minor",
            ],
            [
                "2 - Significant: Minor injury, long term, 1; Significant psych. trauma, 1; Minor inj/psych trauma, 2+",
                "2 - Significant",
            ],
            [
                "3 - Considerable: Severe injury, 1, severe incapacity, recovery expected; Significant psych. trauma, 2+",
                "3 - Considerable",
            ],
            [
                "4 - Major: Death, 1; Severe injury or life-changing incapacity, 1; Psychological trauma, 2+",
                "4 - Major",
            ],
            [
                "5 - Catastrophic: Death, 2+. Severe injury or lifechanging incapacity, 2+",
                "5 - Catastrophic",
            ],
        ),
        "number": ["1", "2", "3", "4", "5"],
    },
    {
        "field_type": "calculate",
        "heading": "### Risk scoring",
        "gui_label": "Risk scoring",
        "text": "1 - Acceptable: Acceptable, no further action required [L1-S1, L1-S2, L2-S1]\n2 - Acceptable: Acceptable if cost of further reduction > benefits, or further risk reduction is impractical [L1-S3, L1-S4, L2-S2, L2-S3, L3-S1, L3-S2, L4-S1]\n3 - Undesirable: Undesirable level of risk. Attempts should be made to eliminate the hazard or implement controls [L1-S5, L2-S4, L3-S3, L3-S4, L4-S2, L4-S3, L5-S1]\n4 - Mandatory-risk-elimination: Mandatory elimination of hazard or addition of controls to reduce risk to an acceptable level [L2-S5, L3-S5, L4-S4, L5-S2, L5-S3]\n5 - Unacceptable: Unacceptable level of risk [L4-S5, L5-S4, L5-S5]",
        "labels": ["L", "S"],
        "choices": {
            "1 - Acceptable: Acceptable, no further action required ": "[L1-S1, L1-S2, L2-S1]",
            "2 - Acceptable: Acceptable if cost of further reduction > benefits, or further risk reduction is impractical ": "[L1-S3, L1-S4, L2-S2, L2-S3, L3-S1, L3-S2, L4-S1]",
            "3 - Undesirable: Undesirable level of risk. Attempts should be made to eliminate the hazard or implement controls ": "[L1-S5, L2-S4, L3-S3, L3-S4, L4-S2, L4-S3, L5-S1]",
            "4 - Mandatory-risk-elimination: Mandatory elimination of hazard or addition of controls to reduce risk to an acceptable level ": "[L2-S5, L3-S5, L4-S4, L5-S2, L5-S3]",
            "5 - Unacceptable: Unacceptable level of risk ": "[L4-S5, L5-S4, L5-S5]",
        },
        "number": ["1", "2", "3", "4", "5"],
    },
    {
        "field_type": "text_area",
        "heading": "### Description",
        "gui_label": "Description",
        "text": "A general description of the Hazard. Keep it short. Detail goes below.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Cause(s)",
        "gui_label": "Cause(s)",
        "text": "The upstream system Cause (can be multiple - use a numbered list) that results in the change to intended care.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Effect",
        "gui_label": "Effect",
        "text": "The change in the intended care pathway resulting from the Cause.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Hazard",
        "gui_label": "Hazard",
        "text": "The potential for Harm to occur, even if it does not.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Harm",
        "gui_label": "Harm",
        "text": "An actual occurrence of a Hazard in the patient or clinical context. This is what we are assessing the Severity and Likelihood of. This is form normal working conditions and fault conditions. Include the ultimate Risk rating as well.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Existing controls",
        "gui_label": "Existing controls",
        "text": "List any pre-existing controls that can mitigate the hazard.",
        "number": [],
    },
    {"field_type": "horizontal_line", "heading": "-----"},
    {
        "field_type": "text_area",
        "heading": "### Assignment",
        "gui_label": "Assignment",
        "text": "Assign this Hazard to its Owner. Default owner is the Clinical Safety Officer",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Labelling",
        "gui_label": "Labelling",
        "text": "Add labels according to Severity. Likelihood and Risk Level",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Project",
        "gui_label": "Project",
        "text": "Add to the Project 'Clinical Risk Management'\nSubsequent discussion can be used to mitigate the Hazard, reducing the likelihood (or less commonly reducing the severity) of the Harm.\nIf Harm is reduced then you can change the labels to reflect this and reclassify the Risk Score.\nIssues can be linked to: Issues describing specific software changes, Pull Requests or Commits fixing Issues, external links, and much more supporting documentation. Aim for a comprehensive, well-evidenced, public and open discussion on risk and safety.",
        "number": [],
    },
    {"field_type": "horizontal_line", "heading": "----- [2]"},
    {
        "field_type": "text_area",
        "heading": "### New hazard controls",
        "gui_label": "New hazard controls",
        "text": "List controls that will be put into place to mitigate the hazard. These can include design, (unit/integration) testing, training or business process change.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Residual hazard risk assessment",
        "gui_label": "Residual hazard risk assessment",
        "text": "Include a repeat analysis of Severity and Likelihood. Include the ultimate Risk rating as well.",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### Hazard status",
        "gui_label": "Hazard status",
        "text": "Either 'open', 'transferred' or 'closed'.",
        "number": [],
    },
    {
        "field_type": "code",
        "heading": "### Code associated with hazard",
        "gui_label": "Code associated with hazard",
        "text": "",
        "labels": [],
        "number": [],
    },
]


ENTRY_INSRTANCE = [
    {"field_type": "icon", "heading": "icon"},
    {
        "field_type": "text_area",
        "heading": "### Hazard name",
        "gui_label": "Hazard name",
        "text": "My first hazard",
        "number": [],
    },
    {
        "field_type": "text_area",
        "heading": "### General Utility label",
        "gui_label": "General utility label",
        "text": "1 - Hazard: A hazard which is logged",
        "number": ["1"],
    },
]

ENTRY_TEMPLATE = [
    {"field_type": "icon", "heading": "icon"},
    {
        "field_type": "text_area",
        "heading": "### Hazard name",
        "gui_label": "Hazard name",
        "text": "A short name",
        "number": [],
    },
    {
        "field_type": "multiselect",
        "heading": "### General Utility label",
        "gui_label": "General utility label",
        "text": "1 - Hazard: A hazard which is logged\n2 - New hazard for triage: A new hazard which needs to be triaged for severity and likelihood, scored and assigned\n3 - Deprecated hazard: A hazard which is no longer considered relevant",
        "labels": [],
        "choices": (
            ["1 - Hazard: A hazard which is logged", "1 - Hazard"],
            [
                "2 - New hazard for triage: A new hazard which needs to be triaged for severity and likelihood, scored and assigned",
                "2 - New hazard for triage",
            ],
            [
                "3 - Deprecated hazard: A hazard which is no longer considered relevant",
                "3 - Deprecated hazard",
            ],
        ),
        "number": ["1", "2", "3"],
    },
]

EXPECTED_FIELD_ADDED_RESULT = [
    {"field_type": "icon", "heading": "icon"},
    {
        "field_type": "text_area",
        "heading": "### Hazard name",
        "gui_label": "Hazard name",
        "text": "My first hazard",
        "number": [],
    },
    {
        "field_type": "multiselect",
        "heading": "### General Utility label",
        "gui_label": "General utility label",
        "text": "1 - Hazard: A hazard which is logged",
        "number": ["1"],
    },
]
