# -*- coding: utf-8 -*-
<%!
    from masterapp.config.include_files import IncludeFiles
%>
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
    % if c.include_files != None:
        % for sheet in c.include_files.stylesheets:
            ${h.stylesheet_link_tag(sheet)}
        % endfor

        <style type="text/css">
        % for template in c.include_files.templated_stylesheets:
            <%include file="${template}" />
        % endfor
        </style>

        % for script in c.include_files.javascripts:
            ${h.javascript_include_tag(script)}
        % endfor
    % endif
</%def>
