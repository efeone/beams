let SHIFTS = [];
let EMPLOYEES = [];
const COLOR_MAP = {
	Blue: "#2490ef",
	Cyan: "#06b6d4",
	Fuchsia: "#d946ef",
	Green: "#22c55e",
	Lime: "#84cc16",
	Orange: "#f97316",
	Pink: "#ec4899",
	Red: "#ef4444",
	Violet: "#8b5cf6",
	Yellow: "#eab308"
};

const state = {
	view: 'weekly',
	currentDate: new Date(),
	assignments: {},
	activeCell: null,
	selectedDepartment: ""
};

function get_week_start(d) {
	const x = new Date(d), day = x.getDay();
	x.setDate(x.getDate() - day + (day === 0 ? -6 : 1));
	x.setHours(0, 0, 0, 0); return x;
}

function get_week_days(d) {
	const s = get_week_start(d);
	return Array.from({ length: 7 }, (_, i) => { const x = new Date(s); x.setDate(s.getDate() + i); return x; });
}

function get_month_days(d) {
	const y = d.getFullYear(), m = d.getMonth(), n = new Date(y, m + 1, 0).getDate();
	return Array.from({ length: n }, (_, i) => new Date(y, m, i + 1));
}

function fmtKey(d) { return d.toISOString().split('T')[0]; }

function fmt_day_name(d) { return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()]; }

function is_today(d) { return d.toDateString() === new Date().toDateString(); }

function cellKey(s, dt) { return `${s}-${dt}`; }

function initials(n) {
	let name = n.split(':')[1]
	return name.split(' ').map(x => x[0]).join('');
}

function get_days() { return state.view === 'weekly' ? get_week_days(state.currentDate) : get_month_days(state.currentDate); }

function get_date_label() {
	if (state.view === 'weekly') {
		const days = get_week_days(state.currentDate), s = days[0], e = days[6];
		const o = { month: 'short', day: 'numeric' };
		return s.getMonth() === e.getMonth()
			? s.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) + ' · Week of ' + s.getDate() + '-' + e.getDate()
			: s.toLocaleDateString('en-US', o) + ' - ' + e.toLocaleDateString('en-US', o) + ', ' + e.getFullYear();
	}
	return state.currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

function set_view(v) {
	state.view = v;
	fetch_shift_assignments().then(() => render());
}

function navigate(dir) {
	const d = new Date(state.currentDate);
	state.view === 'weekly'
		? d.setDate(d.getDate() + dir * 7)
		: d.setMonth(d.getMonth() + dir);

	state.currentDate = d;

	fetch_shift_assignments().then(() => render());
}

function go_to_today() {
	state.currentDate = new Date();
	fetch_shift_assignments().then(() => render());
}

function open_modal(shift_id, date_str, shiftLabel, dateLabel, shift_doc_name) {
	state.activeCell = { shift_id, date_str, shift_doc_name };

	document.getElementById('modal-title').textContent = shiftLabel + ' Shift';
	document.getElementById('modal-subtitle').textContent = dateLabel;
	document.getElementById('emp-search').value = '';
	// IMPORTANT: restore add mode after using View
	document.getElementById('emp-list').style.display = 'block';
	// restore search box too (if hidden later)
	document.getElementById('emp-search').style.display = 'block';
	document.getElementById('modal-backdrop').classList.add('open');

	render_emp_list();
	render_assigned_list();
}

function close_modal() {
	document.getElementById('modal-backdrop').classList.remove('open');
	state.activeCell = null;
}

function viewAssignments(shift_id, date_str, shiftLabel, dateLabel, shift_doc_name) {
	state.activeCell = { shift_id, date_str, shift_doc_name };
	document.getElementById('modal-title').textContent = shiftLabel + ' Shift Assignments';
	document.getElementById('modal-subtitle').textContent = dateLabel;
	// Hide add controls in View mode
	document.getElementById('emp-search').style.display = 'none';
	document.getElementById('emp-list').style.display = 'none';
	document.getElementById('modal-backdrop').classList.add('open');

	render_assigned_list();
}

document.getElementById('emp-list').style.display = 'block';

function handle_backdrop_click(e) {
	if (e.target === document.getElementById('modal-backdrop')) close_modal();
}

function filter_employees() { render_emp_list(); }

function render_emp_list() {
	if (!state.activeCell) return;

	const q = document.getElementById('emp-search').value.toLowerCase();
	const { shift_id, date_str } = state.activeCell;
	const assigned = state.assignments[cellKey(shift_id, date_str)] || [];
	const list = EMPLOYEES.filter(e => e.toLowerCase().includes(q) && !assigned.includes(e));
	const el = document.getElementById('emp-list');

	if (!list.length) { el.innerHTML = '<div class="no-results">No employees found</div>'; return; }

	el.innerHTML = list.map(emp => `
	<div class="emp-item" onclick="assign_emp('${esc(emp)}')">
	  <div class="avatar">${initials(emp)}</div>
	  <span class="emp-name">${emp}</span>
	</div>`).join('');
}

function render_assigned_list() {
	if (!state.activeCell) return;

	const { shift_id, date_str, shift_doc_name } = state.activeCell;
	const assigned = state.assignments[cellKey(shift_id, date_str)] || [];
	const sec = document.getElementById('assigned-section');

	if (!assigned.length) { sec.style.display = 'none'; return; }

	sec.style.display = 'block';
	document.getElementById('assigned-list').innerHTML = assigned.map(emp => `
	<div class="assigned-item">
	  <div class="assigned-left">
		<div class="avatar green sm">${initials(emp)}</div>
		<span class="emp-name">${emp}</span>
	  </div>
	  <button class="remove-btn" onclick="unassign_emp('${esc(emp)}')">&#x2715;</button>
	</div>`).join('');
}

function assign_emp(emp) {
	let emp_id = emp.split(':')[0];
	const { shift_id, date_str, shift_doc_name } = state.activeCell;
	const k = cellKey(shift_id, date_str);
	if (!state.assignments[k]) state.assignments[k] = [];
	if (!state.assignments[k].includes(emp)) state.assignments[k].push(emp);

	create_shift_assignment(shift_doc_name, date_str, emp_id);
	renderTable();
	render_emp_list();
	render_assigned_list();
}
function unassign_emp(emp) {
	let emp_id = emp.split(':')[0];
	const { shift_id, date_str, shift_doc_name } = state.activeCell;
	const k = cellKey(shift_id, date_str);
	if (state.assignments[k]) state.assignments[k] = state.assignments[k].filter(e => e !== emp);

	cancel_shift_assignment(shift_doc_name, date_str, emp_id);
	renderTable();
	render_emp_list();
	render_assigned_list();
}

function esc(s) { return s.replace(/'/g, "\\'"); }

/* ── Table Render ─────────────────────────────────────────────── */
function renderTable() {
	const days = get_days();
	const isMon = state.view === 'monthly';
	const scw = isMon ? 90 : 118;
	const dcw = isMon ? 42 : 94;

	const cols = `<colgroup>
	<col style="width:${scw}px;min-width:${scw}px;">
	${days.map(() => `<col style="width:${dcw}px;min-width:${dcw}px;">`).join('')}
  </colgroup>`;

	const headCells = days.map(d => {
		const td = is_today(d);
		return `<th class="th-day${isMon ? ' monthly' : ''}${td ? ' today' : ''}">
	  <div class="day-name">${fmt_day_name(d)}</div>
	  <div class="day-num">${d.getDate()}</div>
	</th>`;
	}).join('');

	const thead = `<thead><tr>
	<th class="th-shift">Shift</th>
	${headCells}
  </tr></thead>`;

	const rows = SHIFTS.map(sh => {
		const cells = days.map(d => {
			const ds = fmtKey(d);
			const k = cellKey(sh.id, ds);
			const emp = state.assignments[k] || [];
			const lim = isMon ? 1 : 2;
			const chips = emp.slice(0, lim).map(e => {
				const name = isMon ? initials(e) : e.split(' ')[0];
				return `<div class="emp-chip${isMon ? ' monthly' : ''}"
		  style="background:${sh.bg};color:${sh.text};">${name}</div>`;
			}).join('');
			const more = emp.length > lim
				? `<div class="more-count">+${emp.length - lim}</div>` : '';
			const dateLabel = d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
			return `<td class="td-cell">
${chips}${more}

<div style="display:flex;justify-content:center;gap:4px;margin-top:2px;">

${emp.length > 0 ? `
  <button class="add-btn ${isMon ? 'monthly' : 'weekly'}"
	onclick="viewAssignments('${sh.id}','${ds}','${sh.label}','${dateLabel}','${sh.name}')"
	title="View assignments">
	👁
  </button>
` : ''}

<button class="add-btn ${isMon ? 'monthly' : 'weekly'}"
  onclick="open_modal('${sh.id}','${ds}','${sh.label}','${dateLabel}','${sh.name}')"
  title="Assign employee">
  +
</button>

</div>

</td>`;
		}).join('');
		return `<tr>
	  <td class="td-shift" style="border-left:3px solid ${sh.color};">
		<div class="shift-name">
		  <span class="indicator" style="background:${sh.color};"></span>${sh.label}
		</div>
		<div class="shift-time">${sh.time}</div>
	  </td>
	  ${cells}
	</tr>`;
	}).join('');

	document.getElementById('roster-table').innerHTML = cols + thead + `<tbody>${rows}</tbody>`;
}

function renderLegend() {
	document.getElementById('legend-bar').innerHTML = SHIFTS.map(sh =>
		`<div class="legend-item">
	  <div class="legend-dot" style="background:${sh.color};"></div>
	  <span>${sh.label}</span>
	</div>`
	).join('');
}

function updateSummary() {
	const days = get_days();
	const total = days.reduce((acc, d) => {
		return acc + SHIFTS.reduce((a, sh) => {
			return a + (state.assignments[cellKey(sh.id, fmtKey(d))] || []).length;
		}, 0);
	}, 0);
	document.getElementById('summary-label').textContent =
		total > 0 ? `${total} assignment${total !== 1 ? 's' : ''} this ${state.view === 'weekly' ? 'week' : 'month'}` : '';
}

function render() {
	const bw = document.getElementById('btn-weekly');
	const bm = document.getElementById('btn-monthly');
	bw.classList.toggle('active', state.view === 'weekly');
	bm.classList.toggle('active', state.view === 'monthly');
	document.getElementById('date-range-label').textContent = get_date_label();
	document.getElementById('view-indicator').style.background =
		state.view === 'weekly' ? '#2490ef' : '#f8a100';
	renderTable();
	renderLegend();
	updateSummary();
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') close_modal(); });

function hex_to_rbga(hex, opacity = .12) {
	hex = hex.replace('#', '');
	let r = parseInt(hex.substring(0, 2), 16);
	let g = parseInt(hex.substring(2, 4), 16);
	let b = parseInt(hex.substring(4, 6), 16);
	return `rgba(${r},${g},${b},${opacity})`;
}

function loadShifts() {
	return frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Shift Type",
			fields: [
				"name",
				"start_time",
				"end_time",
				"color"
			],
			order_by: "name asc",
			limit_page_length: 100
		}
	}).then(r => {
		SHIFTS = (r.message || []).map(shift => {
			let shiftColor = COLOR_MAP[shift.color] || "#2490ef";
			return {
				name: shift.name,
				id: shift.name.toLowerCase().replace(/\s+/g, '_'),
				label: shift.name,
				time: `${shift.start_time || ''} - ${shift.end_time || ''}`,
				color: shiftColor,
				bg: hex_to_rbga(shiftColor, 0.12),
				text: shiftColor
			};
		});
	});
}

function load_departments() {
	return frappe.call("beams.www.roster.index.get_departments").then(r => {
		let depts = r.message || [];
		let select =
			document.getElementById("department-filter");
		select.innerHTML =
			'<option value="">Select</option>' +
			depts.map(d =>
				`<option value="${d.name}">${d.department_name}</option>`
			).join('');
	});

}

function load_employees() {
	let dept = document.getElementById("department-filter")?.value;
	return frappe.call({
		method: "beams.www.roster.index.get_employees",
		args: {
			department: dept || ''
		}
	}).then(r => {
		EMPLOYEES = (r.message || [])
			.map(e => e.name + ":" + e.employee_name)
			.filter(Boolean);
	});
}

function reload_employees_by_department() {
	load_employees().then(() => {
		fetch_shift_assignments().then(() => {
			render();
		});
	});
}

function create_shift_assignment(shift_doc_name, date_str, emp_id) {
	return frappe.call({
		method: "beams.www.roster.index.create_shift_assignment",
		args: {
			shift_type: shift_doc_name,
			employee: emp_id,
			shift_date: date_str
		}
	});
}

function cancel_shift_assignment(shift_doc_name, date_str, emp_id) {
	return frappe.call({
		method: "beams.www.roster.index.cancel_shift_assignment",
		args: {
			shift_type: shift_doc_name,
			employee: emp_id,
			shift_date: date_str
		}
	});
}

function fetch_shift_assignments() {
	let days = get_days();
	let from_date = fmtKey(days[0]);
	let to_date = fmtKey(days[days.length - 1]);
	let dept = document.getElementById("department-filter")?.value;

	return frappe.call({
		method: "beams.www.roster.index.get_shift_assignments",
		args: {
			from_date: from_date,
			to_date: to_date,
			department: dept || ''
		}
	}).then(r => {
		const assignments = r.message || [];
		state.assignments = {};
		assignments.forEach(a => {
			let shift_id = a.shift_type.toLowerCase().replace(/\s+/g, '_');
			let date_key = fmtKey(new Date(a.start_date));
			let key = cellKey(shift_id, date_key);
			let emp = `${a.employee}:${a.employee_name}`;
			if (!state.assignments[key]) {
				state.assignments[key] = [];
			}
			state.assignments[key].push(emp);
		});
	});
}

$(document).ready(function () {
	$(".web-footer").hide();
	Promise.all([
		loadShifts(),
		load_departments(),
		fetch_shift_assignments()
	]).then(() => {
		return load_employees();
	}).then(() => {
		render();
	});
});