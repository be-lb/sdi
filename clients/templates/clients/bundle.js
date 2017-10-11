(function () { var SDI = Object.create({ {% if user_id %} user: "{{ user_id }}", {% else %} user: null, {% endif %} args: "{{ path }}".split('/'), api : "{{ api }}", csrf : "{{ csrf_token }}", }); var bundle = function defaultMain() { console.error('Bundle not loaded'); }; {% autoescape off %} {{ bundle }} {% endautoescape %}
/* Joined up to here to make mappings correctly point to line numbers */


document.onreadystatechange = function startApplication() {
    if ('interactive' === document.readyState) {
        bundle(SDI);
    }
};

})();
