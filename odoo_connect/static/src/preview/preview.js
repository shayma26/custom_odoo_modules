/** @odoo-module */

import { registry } from "@web/core/registry";
//import { useService } from "@web/core/utils/hooks";

const { Component, onWillUpdateProps, onWillStart, useRef, onMounted } = owl;
export class Preview extends Component {

     parseAndStringify(input) {
        try {
            console.log("input",input)
            // Attempt to parse the input as JSON
            const parsed = JSON.parse(input);

            // If parsing succeeds, stringify it again
            const prettyJSON = JSON.stringify(parsed, null, 4);
            console.log("pretty",prettyJSON)
            return prettyJSON
        } catch (error) {
            // If parsing fails, return the input as it is
            console.log("error",error)
            return input;
        }
    }

    async setup(){
//        this.orm = useService("orm");
        var api_line_model = this.env.model
        this.api_line_data = api_line_model.root.data
        this.targetContainer = useRef("targetContainer");

        onWillUpdateProps((nextProps) => {

            // you can access to other fields in nextProps.record
            this.targetContainer.el.textContent = this.parseAndStringify(nextProps.value);
            Prism.highlightAll()
        });


        onMounted(() => {
                if (this.targetContainer.el) {
                    this.targetContainer.el.textContent = this.parseAndStringify(this.props.value);
                    Prism.highlightAll()
                }
        });

    }

//    async getData() {
//        const domain = this.api_line_data.domain != "" ? eval(this.api_line_data.domain.replace('(','[').replace(')',']')) : []
//        const fields = await this.orm.searchRead('ir.model.fields',[['id','in',this.api_line_data.fields_ids.records.map(item => item.data.id)]],['name'])
//        const fields_names = fields.map(item => item.name)
//        const results = await this.orm.searchRead(this.api_line_data.model_name, domain, fields_names);
//        return fields_names
//    }
}
Preview.template = "odoo_connect.Preview";
Preview.supportedTypes = ["text"];
registry.category("fields").add("preview", Preview);



