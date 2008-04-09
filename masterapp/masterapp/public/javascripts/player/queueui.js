/* These are the custom UI implementations for our tree. The coding style is
 * taken from the ExtJS library instead of what I've been doing elswhere. This
 * is because this style is cleaner when you're just into overriding existing
 * functions and less into extending the actual functionality. --JMT
 */
PlayingNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    // private
    render : function(bulkRender){
        var n = this.node, a = n.attributes;
        var targetNode = n.parentNode ? 
              n.parentNode.ui.getContainer() : n.ownerTree.innerCt.dom;
        
        if(!this.rendered){
            this.rendered = true;
            this.renderElements(n, a, targetNode, bulkRender);
        }else{
            if(bulkRender === true) {
                targetNode.appendChild(this.wrap);
            }
        }
    },
    // private
    renderElements : function(n, a, targetNode, bulkRender){
        // add some indent caching, this helps performance when rendering a large tree
        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';

        var buf = [
            '<li class="x-tree-node">',
            '<div ext:tree-node-id="',n.id,'" class="np-node x-tree-node-leaf x-unselectable ', a.cls,'" unselectable="on">',
                '<div class="np-swatch">',
                    a.swatch ? ('<img src="' + a.swatch + '" />') : '',
                '</div>',
                '<div class="np-title">', a.title, '</div>',
                '<div class="np-info">', a.artist, '</div>',
                '<div class="np-info">', a.album, '</div>',
                '<div id=timeline tabindex="-1"></div>',
            "</div>",
            '<ul class="x-tree-node-ct" style="display:none;"></ul>',
            "</li>"
        ].join('');

        var nel;
        if(bulkRender !== true && n.nextSibling && (nel = n.nextSibling.ui.getEl())){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin", nel, buf);
        }else{
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf);
        }
        this.elNode = this.wrap.childNodes[0];
    },
    updateExpandIcon : Ext.emptyFn,
});

QueueNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    // private
    render : function(bulkRender){
        var n = this.node, a = n.attributes;
        var targetNode = n.parentNode ? 
              n.parentNode.ui.getContainer() : n.ownerTree.innerCt.dom;
        
        if(!this.rendered){
            this.rendered = true;

            this.renderElements(n, a, targetNode, bulkRender);

            if(a.qtip){
               if(this.textNode.setAttributeNS){
                   this.textNode.setAttributeNS("ext", "qtip", a.qtip);
                   if(a.qtipTitle){
                       this.textNode.setAttributeNS("ext", "qtitle", a.qtipTitle);
                   }
               }else{
                   this.textNode.setAttribute("ext:qtip", a.qtip);
                   if(a.qtipTitle){
                       this.textNode.setAttribute("ext:qtitle", a.qtipTitle);
                   }
               } 
            }else if(a.qtipCfg){
                a.qtipCfg.target = Ext.id(this.textNode);
                Ext.QuickTips.register(a.qtipCfg);
            }
            this.initEvents();
        }else{
            if(bulkRender === true) {
                targetNode.appendChild(this.wrap);
            }
        }
    },

    // private
    renderElements : function(n, a, targetNode, bulkRender){
        // add some indent caching, this helps performance when rendering a large tree
        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';

        var cb = typeof a.checked == 'boolean';

        var href = a.href ? a.href : Ext.isGecko ? "" : "#";
        var buf = ['<li class="x-tree-node"><div ext:tree-node-id="',n.id,'" class="x-tree-node-el x-tree-node-leaf x-unselectable ', a.cls,'" unselectable="on">',
            '<span class="x-tree-node-indent">',this.indentMarkup, "</span>",
            '<img src="', this.emptyIcon, '" class="x-tree-ec-icon x-tree-elbow" />',
            '<a hidefocus="on" class="x-tree-node-anchor" href="',href,'" tabIndex="1" ',
            a.hrefTarget ? ' target="'+a.hrefTarget+'"' : "", '><span unselectable="on">',n.text,"</span></a>",
            cb ? ('<input class="x-tree-node-cb qn-cb" type="checkbox" ' + (a.checked ? 'checked="checked" />' : '/>')) : ''
            ,"</div>",
            '<ul class="x-tree-node-ct" style="display:none;"></ul>',
            "</li>"].join('');

        var nel;
        if(bulkRender !== true && n.nextSibling && (nel = n.nextSibling.ui.getEl())){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin", nel, buf);
        }else{
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf);
        }
        
        this.elNode = this.wrap.childNodes[0];
        this.ctNode = this.wrap.childNodes[1];
        var cs = this.elNode.childNodes;
        this.indentNode = cs[0];
        this.ecNode = cs[1];
        this.anchor = cs[2];
        this.textNode = cs[2].firstChild;
        var index = 3;
        if(cb){
            this.checkbox = cs[index];
            index++;
        }
    },

    //private
    getDDHandles : function(){
        return [this.elNode, this.textNode];
    },

    // private
    getDDRepairXY : function(){
        return Ext.lib.Dom.getXY(this.elNode);
    },
    
    //private
    onOver : function(e){
        this.addClass('x-tree-node-over');
        if (this.checkbox)
            Ext.DomHelper.applyStyles(this.checkbox, "visibility: visible");
    },

    //private
    onOut : function(e){
        this.removeClass('x-tree-node-over');
        if (this.checkbox)
            Ext.DomHelper.applyStyles(this.checkbox, "visibility: hidden");
    },
    
});
