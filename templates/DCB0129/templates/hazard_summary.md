---
title: Hazards summary
---
<!-- Cannot have any indentation or these will be misinterpreted by mkdocs -->
{% load custom_filters %}

<!-- This removes the edit icon on the left of the summary bar-->
<style>
.md-typeset summary:before{
    background-color:transparent;

[dir=ltr] .md-typeset .admonition-title, [dir=ltr] .md-typeset summary {
    padding-left: 0rem;
    padding-right: 0rem;
    display: flex;
    align-items: center;
}
}
</style>

# Hazards Summary

{% for hazard in hazards %}
<details markdown="1">
<summary>
<div class="container">
<div class="left">
</div>
<!-- get is a custom filter used in DCSP and returns a value for a key (allows spaces in key) -->
Hazard {{ hazard.number }} - {{ hazard.contents_dict|get:'### Name' }}
<div class="right">
<div>
<img class="hazard" src="../static/hazard/{{ hazard.contents_dict|get:'### General Utility label' }}.png" alt="{{ hazard.contents_dict|get:'### General Utility label' }}">
</div>
<div class="spacer-sm"></div>
<div>
<img class="hazard" src="../static/hazard/{{ hazard.contents_dict|get:'### Likelihood scoring' }}.png" alt="{{ hazard.contents_dict|get:'### Likelihood scoring' }}">
</div>
<div class="spacer-sm"></div>
<div>
<img class="hazard" src="../static/hazard/{{ hazard.contents_dict|get:'### Severity scoring' }}.png" alt="{{ hazard.contents_dict|get:'### Severity scoring' }}">
</div>
<div class="spacer-sm"></div>
<div>
<img class="hazard" src="../static/hazard/{{ hazard.contents_dict|get:'### Risk scoring' }}.png" alt="{{ hazard.contents_dict|get:'### Risk scoring' }}">
</div>
<div class="spacer-md"></div>
</div>
</div>
</summary>
<a href="hazards/hazard-{{ hazard.number }}.html">link to hazard</a><br>
{{ hazard.contents_str }}
</details>
{% endfor %}
