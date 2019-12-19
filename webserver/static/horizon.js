// All date time formatting should happen on the server side. 
// Note for future reference there is a wonderful date time library for JavaScript (overkill here!) called Moment.js
function formatDateTime(date) {
    let d = new Date(date),
        month = (d.getMonth() + 1).toString(),
        day = d.getDate().toString(),
        year = d.getFullYear().toString(),
        hour = d.getHours().toString(),
        minute = d.getMinutes().toString();

    return year + '-' + month.padStart(2, '0') + '-' + day.padStart(2, '0') + ' ' + hour.padStart(2, '0') + ':' + minute.padStart(2, '0');
}
