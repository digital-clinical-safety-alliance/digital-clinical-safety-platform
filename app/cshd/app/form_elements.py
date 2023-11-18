import sys

sys.path.append("/cshd/docs_builder")
from docs_builder import Builder


class formElements:
    def __init__(self) -> None:
        return

    def create_elements(self, placeholders: dict) -> str | None:
        formHTML: str = ""

        for placeholder, value in placeholders.items():
            formHTML += self.wrap_html(
                f'<label for="{ placeholder }">{ placeholder }</label>',
                f'<input type="text" class="inputLarge" id="{ placeholder }" name="{ placeholder }" value="{ value }">',
            )

        return formHTML

    def wrap_html(self, LItem: str = "", RItem: str = "") -> str:
        wrappedHTML: str = f"""        <div class='row'>
            <div class='columnL'>
                { LItem }
            </div>
            <div class='columnR'>
                { RItem }
            </div>
        </div>\n"""

        return wrappedHTML

    def templates_HTML(self):
        templates: list = []
        l_html: str = ""
        r_html: str = ""
        return_html: str = ""

        doc_build = Builder()
        templates = doc_build.get_templates()

        if len(templates) == 0:
            raise Exception(f"No templates found in templates folder!")
            return

        # session["clinicalRequests"] = docxPtr.get_types(lastSelectedLocation)

        l_html = f'<label for="templates">Templates available: </label>'

        r_html += (
            '<select class="templateSelect" name="templates" id="templates">\n'
        )

        for template in templates:
            # if location == lastSelectedLocation:
            #    locationOptionsHTML += f"""<option selected="selected" value="{ location }">{ location }</option>\n"""
            # else:
            r_html += f'<option value="{ template }">{ template }</option>\n'

        r_html += "</select>"

        return_html = self.wrap_html(l_html, r_html)

        return return_html


if __name__ == "__main__":
    test_placeholders = {
        "author_name": "Mark Bailey",
        "project_name": "Clinical Safety Hazard Documentation App",
        "hazard_log_url": "TBC",
        "organisation_name": "Clinicians-Who-Code",
        "clinical_safety_team_name": "Clinicians-Who-Code",
        "clinical_safety_officer_name": "Mark Bailey",
        "clinical_safety_officer_contact": "mark.bailey5@nhs.net",
        "security_responsible_disclosure_email": "mark.bailey5@nhs.net",
        "__project_slug": "TBC",
    }
    form_ptr = formElements()
    print(form_ptr.create_elements(test_placeholders))
