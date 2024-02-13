# How to build templates for DCSP

Outlined below are methods for creating the different templates needed for 
clinical safety documentation.
## How to build an entry template
* Entries are instances of items that you wish to log. For example a hazard or
incident.
* Place in 'CS-documents/templates/[entry name]-template.md'
* Do not use front matter (material between two treble hashes ('---'))
* Headings can use any number hashtags (#)
* Under the heading, the following attributes can be used to change the field 
type:
    * [select] - simple, single selection field on the building site
    * [multiselect] - a multiselect field on building site
    * [calculate] - calculates a view result based on other 'labelled' fields
    (discussed in more detail below).
    * [any_other_values] - used as labels for [calculate] to use.
    * no labels - a simple textarea is used on the building site
* Numbering should be done as
    1 - Line wording
    2 - More line wording
* Do not use 1. 2. 3. as this leads to automatically line numbering that you
will not want when the markdown files are eventually built.
* Anything after a semi colon will be removed from the selection field during
editing, but will be available for the user to see if they click on the 'More
info' help text.

## How are calculate fields calculated
Calculated fields use the values of other 'laballed' fields. These 'labelled'
fields need to be either a select or multiple select field with a label on the
line (under the title) as the select / multiselect attribute: eg

    [select] [label_name]

The calculated field needs the attribute [calculate] under the heading and then
the labels it is to monitor there after, eg:

    [calculate] [labelA] [labelB]

The calculated field should then have a number list (again with "1 -" rather than 
"1."). At the end of each numbered line, there should be a list of combinations
of the monitored fields to match against, a hypthen and then the number of the
item in that monitored field, eg:

    1 - First item [labelA1-labelB1, labelA2-labelB1]
    2 - Second item [labelA3-labelB1, labelA8-labelB1]
    etc...

A javascript script will run each time one of the monitored-labelled field changes
and if it matches the values in the monitored fields, it will update the
calculated field.

## CSS
You need a `icon-small` and a `icon-large` CSS definition for the icons used 
in the entries. `icon-small` is used for the summary pages and `icon-large` is
used for the individual entries.

## Hazard summary page
This is a fairly complicated page, and it would be best to follow examples (need a link).

## Numbering
For lists that are used in selection fields, number lines must be of the form:

number - text

eg

1 - First selection option
2 - Second selection option

## Hazard icons

## Incident templates

## Hazard types

## Officer template

## Complience sign off template


## Documents.yml
Under `entries` add the order you want entries to appear on the Ux. If not supplied 
then these are ordered randomly.