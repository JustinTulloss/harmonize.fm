<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Server Status</title>
</%def>

<%def name="body()">
    <h3> Access Log </h3>
    ${c.accesslog}

    <h3> File Pipeline Log </h3>
    ${c.fplog}

</%def>

