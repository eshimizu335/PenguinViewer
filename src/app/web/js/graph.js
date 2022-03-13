"use strict";
$(document).ready(function() {
let nodeData;

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
}

//tapped node's information
class GeneralInfo{
    constructor(g_evt){
        this.node = g_evt.target;
    }
    showNodeInfoGeneral(){
        console.log("showNodeInfoGeneral");
        $("#hostname").html("ホスト名："+this.node.data("id"));
        $("#ipaddr").html("IPアドレス："+this.node.data("ipaddr"));
        $("#macaddr").html("MACアドレス："+this.node.data("macaddr"));
        $("#model").html("機種："+this.node.data("model"));
        $("#vtp").html("VTPドメイン："+this.node.data("vtp_domain")+", VTPステータス："+this.node.data("vtp_mode"));
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
class InfoTable{
    constructor(i_evt, selectedOption){
        this.div = $("#table_area");
        this.class = "info_table_visible";
        this.nodeData = i_evt.target.data();
        this.selectedOption = selectedOption;
    }
    displayInfoTable(){
        console.log("displayInfoTable");
        if($("#info_table")){
          $("#info_table").remove();
        }
        if($("#no_data")){
            $("#no_data").remove();
        }
        let table = $("<table id = 'info_table'><tbody>");
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

        console.log(command);
        console.log(this.nodeData);
        console.log("commandData↓");
        console.log(commandData);
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
                    //cell.style.backgroundColor = "#D7EEFF";
                }
                else{
                    $("<td>"+dataList[column][1]+"</td>").appendTo(tr);
                    //cell.style.backgroundColor = "#FFFFFF";
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
    cy.on("tap", "node", (evt)=>{
        let generalInfo = new GeneralInfo(evt);
        let showButtonJp = new ShowButton("#show_button_jp", "各種出力(確認したい情報から選ぶ)");
        let showButtonCmd = new ShowButton("#show_button_cmd", "各種出力(コマンドから選ぶ)");
        viewerPage.showRightArea();
        cy.resize();
        cy.fit();
        generalInfo.showNodeInfoGeneral();
        showButtonJp.displayShowButton();
        showButtonCmd.displayShowButton();

        $("#show_button_jp").on("click", ()=>{
            showButtonJp.generateCommandDropdown("Jp");
        });
        $("#show_button_cmd").on("click", ()=>{
            showButtonCmd.generateCommandDropdown("Cmd");
        });

        $(document).on("change", "#command", () =>{
            let infoTable= new InfoTable(evt, $("#command").val());
            infoTable.displayInfoTable();
        });
    });
    $(document).on("click", "#core_apply", () =>{
            let coreName= new CoreName();
            cy.elements().layout(coreName.showHierarchyLayout()).run();
        });
    $(document).on("click", "#clear_button", () =>{
            viewerPage.clearRightArea();
            cy.resize();
            cy.fit();
        });
}
//初回ロード
window.onload = init();
})


