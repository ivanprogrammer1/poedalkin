Vue.component('input--text', {
    props: ['name', 'label'],
    template: `
        <div class="modal--field inputField--text" v-bind:class="addictClass">
            <input type="text" v-bind:name="name" v-model="valueField" @focus="setActive()" @blur="setInactive()">
            <span>{{label}}</span>
        </div>
    `,
    data(){
        return {
            valueField: "",
            active: false,
        }
    },
    methods: {
        setInactive(){
            this.setStatus(false);
        },
        setActive(){
            this.setStatus(true);
        },
        setStatus(status){
            if(this.valueField != "" && status == false){
                return;
            }
            this.active = status;
        }
    },
    computed: {
        addictClass(){
            return this.active == true ? "active" : ""
        }
    }
})

var collectFormData = (form) => {
    let inputs = [...form.querySelectorAll("input")];
    let data = new FormData();
    inputs.map((input, index) => {
        if(input.name != ""){
            data.append(input.name, input.value);
        }
    })
    return data
}

var request = (url, method, data) => {
    return fetch(url, {
        method: method,
        body: data,
        credentials: 'same-origin'
    }).then((value)=>{
        return value.json();
    });
}