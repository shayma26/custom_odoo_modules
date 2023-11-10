/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, onWillUpdateProps, onWillStart, useRef, onMounted } = owl;
export class Preview extends Component {

    async setup(){
        this.orm = useService("orm");
        var api_line_model = this.env.model
        this.api_line_data = api_line_model.root.data

        onWillStart(async() => {
            //this.result = await this.getData();
            });

        onWillUpdateProps((nextProps) => {

            // you can access to other fields in nextProps.record
            this.targetContainer.el.innerHTML = "<code class='language-json'>\n"+nextProps.value+"</code>";
            Prism.highlightAll()
        });

        this.targetContainer = useRef("targetContainer");

        onMounted(() => {
                if (this.targetContainer.el) {
                    this.targetContainer.el.innerHTML = "<code class='language-json'>\n"+this.props.value+"</code>";
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



