// Local variable that keeps track of the selected clinic
var clinic = null;
var start_date = null;
var end_date = null;

$('.datepicker').datepicker({
});

$("#view-stat-btn").click(function (event) {
    // Get the params    
    //clinic = $('select[name=selected_clinic]').val();
    //start_date = $('#id_start_date').val();
    //end_date = $('#id_end_date').val();
	// Calls rendering functions when clinics are selected
	if (clinic) {
		renderEncounterData(clinic);
		renderTestData(clinic);
	} else {
		alert("Select clinic via dropdown menu.")
	}
})

$("li").click(function (event) {
	clinic = $(this).text().trim() // remove whitespace from list
	$("#selected_value").text("Selected clinic: " + clinic);
})


var renderData = function (clinic, start_date, end_date) {

}

var renderEncounterData = function (clinic) {
	// render only the selected clinic's data on the page
	$("#usage-body").html(""); // clear the usage table
	var clinicInfo = usage[clinic];

	//Add day, month, year, all-time
	$("#usage-body").append(
		"<tr>" +
		"<td> Past Day </td>" +
		"<td>" + clinic + "</td>" +
		"<td>" + clinicInfo["day"]["patients"] + "</td>" +
		"<td>" + clinicInfo["day"]["encounters"] + "</td>" +
		"</tr>"
	);

	$("#usage-body").append(
		"<tr>" +
		"<td> Past Month </td>" +
		"<td>" + clinic + "</td>" +
		"<td>" + clinicInfo["month"]["patients"] + "</td>" +
		"<td>" + clinicInfo["month"]["encounters"] + "</td>" +
		"</tr>"
	);

	$("#usage-body").append(
		"<tr>" +
		"<td> Past Year </td>" +
		"<td>" + clinic + "</td>" +
		"<td>" + clinicInfo["year"]["patients"] + "</td>" +
		"<td>" + clinicInfo["year"]["encounters"] + "</td>" +
		"</tr>"
	);

	$("#usage-body").append(
		"<tr>" +
		"<td> All Time </td>" +
		"<td>" + clinic + "</td>" +
		"<td>" + clinicInfo["all-time"]["patients"] + "</td>" +
		"<td>" + clinicInfo["all-time"]["encounters"] + "</td>" +
		"</tr>"
	);
}

var renderTestData = function (clinic, start_date, end_date) {
	// render only the selected clinic's test data on the page 
	$("#diagnosis-body").html(""); // clear the usage table
	var clinicInfo = tests[clinic];

	$("#diagnosis-body").append(
		"<tr>" +
		"<td> Uncontrolled Hypertension </td>" +
		"<td>" + clinicInfo["Hypertension Level"]["Number of Patients"] + "</td>" +
		"<td>" + clinicInfo["Hypertension Level"]["Number of Encounters"] + "</td>" +
		"<td>" + clinicInfo["Hypertension Level"]["Well Managed"] + "</td>" +
		"</tr>"
	);

	$("#diagnosis-body").append(
		"<tr>" +
		"<td> ASCVD Risk Computed (<20%) </td>" +
		"<td>" + clinicInfo["ASCVD Level"]["Number of Patients"] + "</td>" +
		"<td>" + clinicInfo["ASCVD Level"]["Number of Encounters"] + "</td>" +
		"<td>" + clinicInfo["ASCVD Level"]["Well Managed"] + "</td>" +
		"</tr>"
	);

	$("#diagnosis-body").append(
		"<tr>" +
		"<td> Uncontrolled Diabetes </td>" +
		"<td>" + clinicInfo["Diabetes Level"]["Number of Patients"] + "</td>" +
		"<td>" + clinicInfo["Diabetes Level"]["Number of Encounters"] + "</td>" +
		"<td>" + clinicInfo["Diabetes Level"]["Well Managed"] + "</td>" +
		"</tr>"
	);

	$("#diagnosis-body").append(
		"<tr>" +
		"<td> Uncontrolled Dyslipidemia </td>" +
		"<td>" + clinicInfo["Dyslipidemia Level"]["Number of Patients"] + "</td>" +
		"<td>" + clinicInfo["Dyslipidemia Level"]["Number of Encounters"] + "</td>" +
		"<td>" + clinicInfo["Dyslipidemia Level"]["Well Managed"] + "</td>" +
		"</tr>"
	);

    // Clinic drop down controller
}
