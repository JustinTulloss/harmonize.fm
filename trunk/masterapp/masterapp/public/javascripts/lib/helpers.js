function format_time(value)
{

    //Value is the length in milliseconds
    value = Math.floor(value/1000);
    var secs = digitize(value % 60);
    var mins = Math.floor(value / 60 % (60*60));
    var hrs = Math.floor(value / (60*60));

    time = String.format("{0}:{1}", mins, secs);
    if (hrs>0) {
        mins = digitize(mins);
        time = String.format("{0}:{1}:{2}", hrs, mins, secs);
    }
    return time;
}

function digitize(value)
{
    if (value<10)
        return String.format("0{0}", value);
    else return value;
}    
