# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <head>
    ${self.head_tags()}
    ${h.javascript_include_tag(builtins=False)}
  </head>
  <body>
    ${self.body()}
        <script type="text/javascript">
    var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
    document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
    </script>
    <script type="text/javascript">
    var pageTracker = _gat._getTracker("UA-3660713-1");
    pageTracker._initData();
    pageTracker._trackPageview();
    </script>
  </body>
</html>

<%def name="head_tags()">
    <title>Override this title!</title>
</%def>
