function get_browser_data()
{
    var data = {
        browser: {
            appCodeName: navigator.appCodeName,
            appName: navigator.appName,
            appVersion: navigator.appVersion,
            buildID: navigator.buildID,
            cookieEnabled: navigator.cookieEnabled,
            language: navigator.language,
            onLine: navigator.onLine,
            oscpu: navigator.oscpu,
            platform: navigator.platform,
            product: navigator.product,
            productSub: navigator.productSub,
            securityPolicy: navigator.securityPolicy,
            userAgent: navigator.userAgent,
            vendor: navigator.vendor,
            vendorSub: navigator.vendorSub
        },
        screen: screen
    }
    return Ext.util.JSON.encode(data);
}

function format_time(value)
{

    //Value is the length in milliseconds
    value = Math.floor(value/1000);
    var secs = digitize(value % 60);
    var mins = Math.floor(value / 60 % (60*60));
    var hrs = Math.floor(value / (60*60));

    if (hrs>0) {
        mins = digitize(mins);
        time = String.format("{0}:{1}:{2}", hrs, mins, secs);
    }
	else
		time = String.format("{0}:{1}", mins, secs);
    return time;
}

function digitize(value)
{
    if (value<10)
        return String.format("0{0}", value);
    else return String(value, 10);
}    

function untyped_record(response) {
	var res = eval('(' + response.responseText + ')');
	var record = res.data[0];
	record.get = function(key) {return record[key];};
	record.set = function(key, val) {record[key] = val;};
	return record;
}

//Determines whether the current user is the owner of a given record
function own_record(record) {
	return record.get('Friend_id') === global_config.uid ||
			record.get('Friend_id') === '';
}
