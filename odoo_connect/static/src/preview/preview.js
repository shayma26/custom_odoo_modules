/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, onWillUpdateProps, onWillStart, useRef, onMounted } = owl;
export class Preview extends Component {

    async setup(){
        this.orm = useService("orm");
        var api_line_model = this.env.model
        this.api_line_data = api_line_model.root.data
        this.targetContainer = useRef("targetContainer");

//        onWillStart(() => {
//            if (this.targetContainer.el) {
//                this.targetContainer.el.value = this.props.value;
//                Prism.highlightAll()
//                }
//            });

        onWillUpdateProps((nextProps) => {

            // you can access to other fields in nextProps.record
            console.log("update props", nextProps.value)
            this.targetContainer.el.textContent = nextProps.value;
            Prism.highlightAll()
        });


        onMounted(() => {
                if (this.targetContainer.el) {
                    console.log("mounted", this.props.value)
                    this.targetContainer.el.textContent = this.props.value;
                    Prism.highlightAll()
                }
        });

    }

    async getData() {
        const domain = this.api_line_data.domain != "" ? eval(this.api_line_data.domain.replace('(','[').replace(')',']')) : []
        const fields = await this.orm.searchRead('ir.model.fields',[['id','in',this.api_line_data.fields_ids.records.map(item => item.data.id)]],['name'])
        const fields_names = fields.map(item => item.name)
        const results = await this.orm.searchRead(this.api_line_data.model_name, domain, fields_names);
        return fields_names
    }


}
Preview.template = "odoo_connect.Preview";
Preview.supportedTypes = ["text"];
registry.category("fields").add("preview", Preview);



