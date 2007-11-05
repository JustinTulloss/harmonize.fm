# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <head>
    ${self.head_tags()}
    ${h.javascript_include_tag(builtins=True)}
  </head>
  <body>
    ${self.body()}
  </body>
</html>

<%def name="head_tags()">
    <title>Override this title!</title>
</%def>