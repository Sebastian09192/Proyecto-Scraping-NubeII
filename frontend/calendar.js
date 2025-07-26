// frontend/calendar.js
document.addEventListener("DOMContentLoaded", function() {
    // Cambia la ruta según dónde corras tu http.server (a veces es necesario ajustar)
    fetch("data/events.json")
        .then(resp => resp.json())
        .then(eventos => {
            const calendarEl = document.getElementById('calendar');
            if (!calendarEl) return;
            // Convierte eventos a formato FullCalendar (puedes personalizarlo más)
            const eventosCalendar = eventos.map(ev => ({
                title: ev.title,
                start: ev.timestamp,
                description: ev.descripcion || "",
                tipo: ev.tipo || "evento"
            }));

            // Usando FullCalendar v3
            $('#calendar').fullCalendar({
                events: eventosCalendar,
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay'
                },
                eventClick: function(event) {
                    alert(
                        `Título: ${event.title}\n` +
                        `Descripción: ${event.description}\n` +
                        `Tipo: ${event.tipo}`
                    );
                }
            });
        })
        .catch(e => {
            console.error("Error cargando eventos:", e);
        });
});