<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Create New Blog Entry</title>
</%def>

<%def name="body()">
    <center>
    <h1>Post to Front Page</h1>
    ${h.html.tags.form('postblog', method='POST')}
        <div>Title: ${h.html.tags.text('title', size=100, maxlength=255)}</div>
        <div>Author: ${h.html.tags.text('author', size=100, maxlength=255)}</div>
        <div>Entry: ${h.html.tags.textarea('entry', size='100x15')}</div>
        <div>${h.html.tags.submit(value='Post', name='post')}</div>
    ${h.html.tags.end_form()}
    </center>
</%def>
