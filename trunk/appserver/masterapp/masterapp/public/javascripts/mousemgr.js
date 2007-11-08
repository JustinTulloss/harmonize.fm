/* Justin Tulloss
 *
 * This script manages mouseover actions. It's fun.
 */

function MouseMgr()
{
    var regularimgs = Array();
    var overimgs = Array();
    var clickimgs = Array();

    this.processImages = processImages;
    this.loadImage = loadImage;
    this.mouseover = mouseover;
    this.mousedown = mousedown;
    this.mouseout = mouseout;

    this.processImages();

    function processImages()
    {
        var imgTags = Ext.select("img");
        imgTags.on("mouseover", this.mouseover);
        imgTags.on("mousedown", this.mousedown);
        imgTags.on("mouseout", this.mouseout);
        imgTags.each(this.loadImage);
    }

    function loadImage(img)
    {
        img.id = Ext.id(img); //Checks to see if it has an id, assigns one if it doesn't

        var suffix = img.dom.src.substring(img.dom.src.lastIndexOf('.'));
        /*save off original*/
        regularimgs[img.id] = new Image();
        regularimgs[img.id].src = img.dom.src;
        /*Try to load mouseover */
        overimgs[img.id] = new Image();
        overimgs[img.id].src = 
            img.dom.src.substring(0,img.dom.src.lastIndexOf('.'))+"_over"+suffix;
        /*Try to load mousedown */
        clickimgs[img.id] = new Image();
        clickimgs[img.id].src = 
            img.dom.src.substring(0,img.dom.src.lastIndexOf('.'))+"_click"+suffix;
    }

    function mouseover(e)
    {
        //our scope is the image itself
        this.src = overimgs[this.id].src;
    }

    function mouseout(e)
    {
        if (this.src != null)
            this.src = regularimgs[this.id].src;
    }
    
    function mousedown(e)
    {
        if (this.src != null)
            this.src = clickimgs[this.id].src;
    }
}
