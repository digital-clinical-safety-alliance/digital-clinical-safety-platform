---
title: Hazards summary
---

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

{% for hazard in entries %}
<details markdown="1">
<summary>
<div class="container">
<div class="left">
</div>

Hazard {{ hazard.number }} -
{% for dict in hazard.contents_list %}{% if dict.heading == "### Hazard name" %}{{ dict.text }}{% endif %}{% endfor %}

<div class="right">

{{ hazard.icon_html }}

</div>
</div>
</summary>
<a href="hazards/hazard-{{ hazard.number }}.html">link to hazard</a><br>

{{ hazard.contents_str }}
</details>
{% endfor %}
