<%inherit file="base.mako" />

<%def name="head_tags()">
    <title>Rubicon Admin</title>
</%def>

<%def name="body()">
    <h3>Rubicon Admin Interface</h3>
    <ul>
        <li><a href='admin/rmentities'>Clean Database</a></li>
        <li><a href='admin/s3cleanup'> Clean S3</a></li>
    </ul>
</%def>