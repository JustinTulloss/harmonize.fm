/* Justin Tulloss
 * 03/11/2008
 *
 */

/* Handles displaying errors in a nice way. Also handles logging. */
function ErrorManager()
{
    var t_errcontents = new Ext.Template('<span>{message}</span>');
    t_errcontents.compile();

    var levels = {DEBUG:0, INFO:1, WARN:2, ERROR:3, EXCEPTION:4};

    /* An info error is an error that will go away after 5 seconds
     * and requires no recovery steps from the user
     */
    this.info = info;
    function info(options)
    {
        Ext.Msg.show({
            animEl: 'top',
            closable: true,
            msg: options.message,
            buttons: Ext.Msg.OK,
            modal: false,
            width: 500,
            height: 100,
            icon: Ext.Msg.INFO
        });

        Ext.Msg.hide.defer(5000, Ext.Msg);
    }

    /* An warning error is an error that will not go away, but
     * requires no recovery steps from the user
     */
    this.warn = warn;
    function warn(options)
    {
        Ext.Msg.show({
            animEl: 'top',
            closable: true,
            msg: options.message,
            buttons: Ext.Msg.OK,
            modal: false,
            width: 500,
            height: 100,
            icon: Ext.Msg.WARN
        });
    }

    /* An error is an unrecoverable error that requires user interaction. */
    this.error = error;
    function error(options)
    {
        Ext.Msg.show({
            animEl: 'top',
            closable: true,
            msg: options.message,
            buttons: Ext.Msg.OK,
            modal: true,
            width: 500,
            height: 100,
            icon: Ext.Msg.ERROR
        });
    }
}
