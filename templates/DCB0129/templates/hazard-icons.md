<div class="right">
{% for dict in contents_list %}{% if dict.heading == "### General Utility label" %}{% for number in dict.number %}
<div>
<img class="icon-large" src="../../static/hazard/general-{{ number }}.png" alt="General icon">
</div>
<div class="spacer-sm"></div>
{% endfor %}{% endif %}{% endfor %}

<div>
{% for dict in contents_list %}{% if dict.heading == "### Likelihood scoring" %}
<img class="icon-large" src="../../static/hazard/likelihood-{{ dict.number[0] }}.png" alt="Likelihood icon">
{% endif %}{% endfor %}
</div>

<div class="spacer-sm"></div>

<div>
{% for dict in contents_list %}{% if dict.heading == "### Severity scoring" %}
<img class="icon-large" src="../../static/hazard/severity-{{ dict.number[0] }}.png" alt="Severity icon">
{% endif %}{% endfor %}
</div>

<div class="spacer-sm"></div>

<div>
{% for dict in contents_list %}{% if dict.heading == "### Risk scoring" %}
<img class="icon-large" src="../../static/hazard/risk-{{ dict.number[0] }}.png" alt="Risk icon">
{% endif %}{% endfor %}
</div>

<div class="spacer-md"></div>
</div>