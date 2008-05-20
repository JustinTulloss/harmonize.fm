<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>Create New Blog Entry</title>
</%def>

<%def name="body()">
    <center>
    <h1>Post to Front Page</h1>
    ${h.rails.form('postblog', method='POST')}
        <div>Title: ${h.rails.text_field('title', size=100, maxlength=255)}</div>
        <div>Author: ${h.rails.text_field('author', size=100, maxlength=255)}</div>
        <div>Entry: ${h.rails.text_area('entry', size='100x15')}</div>
        <div>${h.rails.submit(value='Post', name='post')}</div>
    ${h.rails.end_form()}
    </center>
</%def>
