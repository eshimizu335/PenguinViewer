"use strict";
$(document).ready(function() {
let nodeData;
let nodeLabel = "hostname";

class ViewerPage{
    constructor(){
        this.left = $("#left")
        this.right = $("#right")
    }
    showRightArea(){
        this.left.removeClass("left_wide");
        this.left.addClass("left_narrow");
        this.right.removeClass("right_narrow");
        this.right.addClass("right_wide");
    }
    clearRightArea(){
        this.left.removeClass("left_narrow");
        this.left.addClass("left_wide");
        this.right.removeClass("right_wide");
        this.right.addClass("right_narrow");
    }
}

//Network Graph
class GraphData{
    constructor(){
        this.elements = eel.generate_graph_data()();
        this.layout = {name:"grid"};
        this.defaultStyle = eel.define_graph_style("default")();
        this.flowerStyle = eel.define_graph_style("flower")();
        this.universeStyle = eel.define_graph_style("universe")();
    }
}
//core hostname for hierarchy layout
class CoreName{
    constructor(){
        this.name = $("#core_hostname").val();
    }
    showHierarchyLayout(){
        let hLayout = {
            "name":"breadthfirst",
            "roots":"#"+this.name
        }
    return hLayout;
    }
    getCoreSelector(){
        return "#"+this.name;
    }
}

//tapped node's information
class GeneralInfo{
    constructor(g_evt){
        this.node = g_evt.target;
    }
    showNodeInfoGeneral(){
        console.log("showNodeInfoGeneral");
        $("#hostname").html(this.node.data("id"));
        $("#ipaddr").html(this.node.data("ipaddr"));
        $("#macaddr").html(this.node.data("macaddr"));
        $("#model").html(this.node.data("model"));
        $("#vtp").html(this.node.data("vtp_domain"));
        $("vtp_s").html(this.node.data("vtp_mode"));
    }
}

class ShowButton{
    constructor(id, label){
        this.id = id;
        this.class = "show_button";
        this.label = label;
    }
    displayShowButton(){
        $(this.id).removeClass("invisible");
        $(this.id).addClass(this.class);
        $(this.id).text(this.label);
    }
    generateCommandDropdown(c_order){
        let commandDropdown = new CommandDropdown(c_order);
        commandDropdown.displayCommandDropdown();
    }
}
//command dropdown
class CommandDropdown{
    constructor(d_order){
        this.id = "#command";
        this.class = "command_dropdown_visible";
        this.order = d_order; //Jp or Cmd
        this.jpOptions = [
            {value:"", label:"確認したい情報を選択"},
            {value:"cdp", label:"隣接機器情報"},
            {value:"interface_status", label:"ポートステータス"},
            {value:"int_brief", label:"IPインターフェース情報"},
            {value:"ip_route", label:"ルーティングテーブル"},
            {value:"mac_table", label:"MACアドレステーブル"},
            {value:"ip_arp", label:"arp情報"},
        ];
        this.cmdOptions = [
            {value:"", label:"コマンドを選択"},
            {value:"cdp", label:"show cdp neighbors"},
            {value:"interface_status", label:"show interfaces status"},
            {value:"int_brief", label:"show ip interface brief"},
            {value:"ip_route", label:"show ip route"},
            {value:"mac_table", label:"show mac-address-table"},
            {value:"ip_arp", label:"show ip arp"},
        ];
    }
    displayCommandDropdown(){
        $(this.id).find("option").remove();
        if (this.order === "Jp"){
            $.each(this.jpOptions, (i)=>{
                $(this.id).append($("<option></option>")
                    .val(this.jpOptions[i].value)
                    .text(this.jpOptions[i].label));
            });
        }
        else{
             $.each(this.cmdOptions, (i)=>{
                $(this.id).append($("<option></option>")
                    .val(this.cmdOptions[i].value)
                    .text(this.cmdOptions[i].label));
            });
        }
        $(this.id).removeClass("invisible");
        $(this.id).addClass(this.class);
    }
}
//output table
class OutputTable{
    constructor(i_evt, selectedOption){
        this.div = $("#table_area");
        this.class = "output_table_visible";
        this.nodeData = i_evt.target.data();
        this.selectedOption = selectedOption;
    }
    displayOutputTable(){
        console.log("displayOutputTable");
        if($("#output_table")){
          $("#output_table").remove();
        }
        if($("#no_data")){
            $("#no_data").remove();
        }
        let table = $("<table id = 'output_table'><tbody>");
        let command = this.selectedOption;  //いる？
        let commandData;
        if(command === "cdp"){
            commandData = this.nodeData.cdp;
            console.log("command is cdp.");
        }
        else if(command === "interface_status"){
            commandData = this.nodeData.interface_status;
            console.log("command is interface_Status");
        }
        else if(command === "int_brief"){
            commandData = this.nodeData.int_brief;
            console.log("command is int brief");
        }
        else if(command === "ip_route"){
            commandData = this.nodeData.ip_route;
            console.log("command is ip_route");
        }
        else if(command === "mac_table"){
            commandData = this.nodeData.mac_table;
            console.log("command is mac_table");
        }
        else if(command === "ip_arp"){
            commandData = this.nodeData.ip_arp;
            console.log("command is ip_arp");
        }
        else{
            commandData = this.nodeData.cdp;
            console.log("command not found");
        }

        if(commandData === undefined || commandData.length === 0){
            return $("<h2 id = 'no_data'>データがありません</h2>").insertAfter($("#command"));
        }


        let dataListStr = JSON.stringify(commandData);
        let tmpList = JSON.parse(dataListStr);

        console.log("tmpList:"+tmpList);
        for (let row = -1; row<commandData.length; row++){
            let dataList;
            let tr = $("<tr></tr>").appendTo(table);
            if (row === -1){   //th
                dataList = Object.entries(tmpList[row+1]);
            }else{  //tr
                dataList = Object.entries(tmpList[row]);
            }
            console.log("dataList"+dataList);
            for(let column = 0; column < dataList.length; column++){
                if (row === -1){
                    $("<th>"+dataList[column][0]+"</th>").appendTo(tr);
                }
                else{
                    $("<td>"+dataList[column][1]+"</td>").appendTo(tr);
                }
            }
        }
        this.div.append(table);
        $(this.div).removeClass("invisible");
        table.addClass(this.class);
    }
}


const init = ()=>{
    let viewerPage = new ViewerPage;
    let graphData = new GraphData();
    let cy = cytoscape({
            container:$("#graph"),
            elements:graphData.elements,
            style:graphData.defaultStyle,
            layout:graphData.layout,
        });
    $(document).on("change", "#theme", async () =>{
        let newStyle;
        if ($("#theme").val() === "flower"){
            newStyle = await graphData.flowerStyle;
        }
        else if ($("#theme").val() === "universe"){
            newStyle = await graphData.universeStyle;
        }
        else{
            newStyle = await graphData.defaultStyle;
            }
        cy.style().clear().fromJson(newStyle).update();
    });
    cy.on("mouseover","node", (evt)=>{
        let node = evt.target;
        let nodeSelector = "#"+node.data("id");
        if (nodeLabel === "hostname"){
            cy.style().selector(nodeSelector).style("content", "data(ipaddr)").update();
        }
        else if (nodeLabel === "ipaddr"){
            cy.style().selector(nodeSelector).style("content", "data(id)").update();
        }
        cy.$(nodeSelector).addClass("hover");
    })
    cy.on("mouseout","node", (evt)=>{
        let node = evt.target;
        let nodeSelector = "#"+node.data("id");
        if (nodeLabel === "hostname"){
            cy.style().selector(nodeSelector).style("content", "data(id)").update();
        }
        else if (nodeLabel === "ipaddr"){
            cy.style().selector(nodeSelector).style("content", "data(ipaddr)").update();
        }
        cy.$(nodeSelector).removeClass("hover");
    })
    cy.on("tap", "node", (evt)=>{
        let node = evt.target;
        let nodeSelector = "#"+node.data("id");
        let generalInfo = new GeneralInfo(evt);
        let showButtonJp = new ShowButton("#show_button_jp", "各種出力(確認したい情報から選ぶ)");
        let showButtonCmd = new ShowButton("#show_button_cmd", "各種出力(コマンドから選ぶ)");
        viewerPage.showRightArea();
        cy.resize();
        cy.fit();
        generalInfo.showNodeInfoGeneral();
        showButtonJp.displayShowButton();
        showButtonCmd.displayShowButton();

        cy.$("node").removeClass("tap");
        cy.$(nodeSelector).addClass("tap");

        $("#show_button_jp").on("click", ()=>{
            showButtonJp.generateCommandDropdown("Jp");
        });
        $("#show_button_cmd").on("click", ()=>{
            showButtonCmd.generateCommandDropdown("Cmd");
        });

        $(document).on("change", "#command", () =>{
            let outputTable= new OutputTable(evt, $("#command").val());
            outputTable.displayOutputTable();
        });
    });
    $(document).on("click", "#core_apply", () =>{
            let coreName= new CoreName();
            cy.elements().layout(coreName.showHierarchyLayout()).run();
            cy.$(coreName.getCoreSelector()).addClass("core");  // change core colour

    });
    $(document).on("click", "#clear_button", () =>{
            viewerPage.clearRightArea();
            cy.$("node").removeClass("tap");
            cy.resize();
            cy.fit();
    });

    $(document).on("click", "#hostname_apply", () =>{
            cy.style().selector("node").style("content", "data(id)").update();
            nodeLabel = "hostname";
    });

    $(document).on("click", "#ipaddr_apply", () =>{
            cy.style().selector("node").style("content", "data(ipaddr)").update();
            nodeLabel = "ipaddr";
    });
}
//初回ロード
window.onload = init();
})


