<%inherit file="base.mako" />

<%def name="head_tags()">
    <title>Rubicon Admin</title>
</%def>

<%def name="body()">
    <h3>Rubicon Admin Interface</h3>
    <ul>
        <li><a href='admin/rmentities'>Clean Database</a></li>
        <li><a href='admin/s3cleanup'>Clean S3</a></li>
        <li><a href='admin/monitor'>Monitor Server Status</a></li>
        <li><a href='admin/blog'>Post Blog Entry</a></li>
        <li><a href='admin/monitor_pipeline'>Monitor Pipeline</a></li>
        <li><a href='admin/manage_whitelist'>Manage Whitelist</a></li>
    </ul>
</%def>
