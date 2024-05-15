import React,{ useState} from 'react'
import redashpng from "@/assets/images/bot.png";
import './chatbox.less'
import Chat from '@/services/chat';
import { Query } from '@/services/query';
import { axios } from "@/services/axios";
import { IoCopy } from "react-icons/io5";
import { FaCheck } from "react-icons/fa6";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import copy from 'copy-to-clipboard';
import { forEach, random } from 'lodash';


export default function ChatBox() {
  const [input, setInput] = useState("")
  const [open, setOpen] = useState(false);
  const [copiedStates, setCopiedStates] = useState({});
  const [chatHistory, setChatHistory] = useState([]);

  const handler = (event) => {
    if (event.keyCode === 13) {      
      handleChatInput();
    }
  };
  function extractColumnNames(sqlQuery) {
    const columnNames = [];
    const regex = /SELECT\s+(.*?)\s+FROM/gi;
    const aliasRegex = /\s+AS\s+(\w+)/gi;
    
    const selectClause = regex.exec(sqlQuery)[1];
    
    const columns = selectClause.split(',');
    
    columns.forEach(column => {
        column = column.trim();
        const aliasMatch = aliasRegex.exec(column);
        if (aliasMatch) {
            columnNames.push(aliasMatch[1]);
        } else {
            columnNames.push(column.replace(/["']/g, '').trim());
        }
        aliasRegex.lastIndex = 0;  // Reset the regex index for the next iteration
    });

    return columnNames;
  }

  function generateChartOptions(params) {
    const {
        name,
        qry_id,
        desc,
        columns,
        size_column,
        group_by,
        _type,
        custom_options
    } = params;

    if (!_type) {
        throw new Error("Type is required.");
    }

    const columnMapping = {};
    const seriesOptions = {};

    // The first column is the X axis
    const x_axis = columns[0];

    // The rest of the columns are Y axes
    const y_axis = columns.slice(1).map((col, idx) => ({
        name: col,
        label: col,
        type: _type
    }));

    y_axis.forEach((y, idx) => {
        if (!y.name) {
            throw new Error("name is required in y_axis.");
        }

        const y_name = y.name;
        const y_label = y.label || y_name;
        const y_type = y.type || _type;

        columnMapping[y_name] = "y";
        seriesOptions[y_name] = {
            index: 0,
            type: y_type,
            name: y_label,
            yAxis: 0,
            zIndex: idx
        };
    });

    if (size_column !== null) {
        columnMapping[size_column] = "size";
    }

    if (group_by !== null) {
        columnMapping[group_by] = "series";
    }

    const chart_type = 'CHART';
    const options = {
        globalSeriesType: _type,
        sortX: true,
        legend: { enabled: true },
        yAxis: [{ type: "linear" }, { type: "linear", opposite: true }],
        xAxis: { type: "category", labels: { enabled: true } },
        error_y: { type: "data", visible: true },
        series: { stacking: null, error_y: { type: "data", visible: true } },
        columnMapping: { [x_axis]: "x", ...columnMapping },
        seriesOptions: seriesOptions,
        showDataLabels: _type === 'pie',
        ...custom_options
    };

    return {
        name: name,
        type: chart_type,
        query_id: qry_id,
        description: desc,
        options: options
    };
  }

  function handleChatInput() {
    const data = { sender: "user", text: input };
    if (input !== "") {
      setChatHistory((history) => [...history, data]);
      chatWithOpenai(input);    
      setInput("");  
    }
  }

  async function chatWithOpenai(text) {
    const requestOptions = {
        question: text
    };
    const response = await Chat.openai(requestOptions);
    const chat_data = {
      sender: "bot",
      text: response.answer
    };
    console.log("The Answer is :: " + response.answer);

    setChatHistory((history) => [...history, chat_data]);

    setInput("");
    
    const query_params = {   
      "data_source_id": 1,   // Replace with the actual data source ID
      "name": getWords(text, 5), // extract the first 5 words from the text and use them as the query name
      "query": response.answer,
      "description": text,
      "options": {},
    }
    const getQuery = query => new Query(query);
    const saveOrCreateVizualizationUrl = data => (data.id ? `api/visualizations/${data.id}` : "api/visualizations");
    const saveOrCreateUrl = data => (data.id ? `api/queries/${data.id}` : "api/queries");
    
    const query = await axios.post(saveOrCreateUrl(query_params), query_params)

    console.log("The Query is :: ", query);

    // Get Column Names From SQL query for Visualization
    const columns = extractColumnNames(response.answer);

    console.log("The Columns are ::", columns); // Output: ["City name", "total_views"]

    // Example usage:
    const chart_params = {
      name: `${columns[0]} vs. ${columns[1]}`, // make the name dynamic by using the column names 
      qry_id: query.id,
      desc: "Chart for " + text,
      columns: columns,
      size_column: null,
      group_by: null,
      _type: "column", // TODO make chart types available by LLM to best choose the type for the SQL chart
      custom_options: { color: "red" }
    };

    const chart_viz_payload = generateChartOptions(chart_params);

    console.log("The Payload is ::",chart_viz_payload);

    const viz = await axios.post(saveOrCreateVizualizationUrl(chart_viz_payload), chart_viz_payload)

    console.log("The Visualization is ::",viz);

    await axios.post(`api/queries/${query.id}/refresh`); 

    const dashboard = await axios.post(`api/dashboards`, {"name":`Dashboard_${getWords(text, 5).split(' ').join('_')}`});
    
    const widget_payload = {
      "dashboard_id": dashboard.id,
      "text": "My Text For Widget",
      "visualization_id": viz.id,
      "width": 1,
      "options": {
          "position": calculateWidgetPosition(dashboard.id, false),
      }
    }

    axios.post('api/widgets', widget_payload)
  }

  function getWords(sentence, num) {
    // Split the sentence into an array of words using a space as the delimiter
    const words = sentence.split(' ');

    // Slice the first 5 words from the array
    const firstFiveWords = words.slice(0, num);

    // Join the first 5 words back into a string (if you need the result as a string)
    const result = firstFiveWords.join(' ');

    return result;
  }
  async function calculateWidgetPosition(dbId, fullWidth) {
    const resDashboards = await axios.get('api/dashboards');
    const dashboards = resDashboards.results || [];
    const slug = dashboards.find(d => d.id === dbId)?.slug;

    if (!slug) {
        throw new Error(`Dashboard with id ${dbId} not found`);
    }

    const resDashboard = await axios.get(`api/dashboards/${slug}`);
    const widgets = resDashboard.widgets || [];

    let exceedHalfWidthWidgetsCount = 0;

    widgets.forEach(w => {
        if (w.options.position.col + w.options.position.sizeX > 3) {
            exceedHalfWidthWidgetsCount += 1;
        }
    });

    let position = {
        col: 0,
        row: 0,
        sizeX: 3,
        sizeY: 8
    };

    if (widgets.length > 0) {
        const len = widgets.length - exceedHalfWidthWidgetsCount;
        const row = Math.floor(len / 2);
        const col = len % 2;

        position.col = col * 3;
        position.row = (row + exceedHalfWidthWidgetsCount) * 8;
    }

    if (fullWidth) {
        position.col = 0;
        position.sizeX = 6;
    }

    return position;
  }
  const handleCopy = (content) => {
    copy(content);
    const updatedCopiedStates = { ...copiedStates };
    updatedCopiedStates[content] = true;
    setCopiedStates(updatedCopiedStates);

    setTimeout(() => {
      const revertedCopiedStates = { ...copiedStates };
      revertedCopiedStates[content] = false;
      setCopiedStates(revertedCopiedStates);
    }, 2000); // Change the duration (in milliseconds) as needed
  };

  const formatingCode = (code) => {
    // Split the code by lines to remove unnecessary white spaces
    const lines = code.split(/\s*(?=<)/);
    
    // Remove leading and trailing white spaces from each line
    const trimmedLines = lines.map((line) => line.trim());
    
    // Join the lines with line breaks and indentation
    const formattedCode = trimmedLines.join('\n');
    
    return formattedCode;
  };

  const splitAnswerParts = (answer) => {
    const parts = [];
    const codeRegex = /```([\s\S]*?)```/g;
  
    let match;
    let lastIndex = 0;
  
    while ((match = codeRegex.exec(answer))) {
      const codeContent = match[1].trim();
  
      if (match.index > lastIndex) {
        const textContent = answer.substring(lastIndex, match.index).trim();
        parts.push({ type: 'text', content: textContent });
      }
  
      const lines = codeContent.split('\n');
      const firstLine = lines[0].trim();
      const firstWord = firstLine.split(' ')[0];
      const firstLineEndIndex = codeContent.indexOf(' ') + 1;
      const remainingCode = codeContent.substring(firstLineEndIndex).trim();
      const formattedCodeContent = formatingCode(remainingCode); // Process the remaining code through formatingCode function
  
      parts.push({ type: 'code', firstWord, content: formattedCodeContent });
  
      lastIndex = match.index + match[0].length;
    }
  
    if (lastIndex < answer.length) {
      const textContent = answer.substring(lastIndex).trim();
      parts.push({ type: 'text', content: textContent });
    }
  
    return parts;
  };

  
  return (
    <>
      {open?
      <div className='chatcontainer'>
        <div>
            <div className='headbox'>
              <p>query, visualize with AI</p>            
            </div>

            <div className='chatbox'>
              {chatHistory.map((chat, index) => (
                <div key={index} className="chatcontain">
                  {chat.sender === "user" ? (
                    <div className="user">
                      <div className="">
                        <p className="parauser">{chat?.text}</p>
                      </div>
                    </div>
                  ) : (
                    <div className='ai'>
                      <div className="">
                        {chat?.text && (
                          <div>
                            {splitAnswerParts(chat.text).map((part, partIndex) => (
                              <React.Fragment key={partIndex}>
                                {part.type === 'code' ? (
                                  <div className="">
                                    <div className='chat-head'>
                                        <div className='copy' onClick={() => handleCopy(part.content)}>
                                          {copiedStates[part.content] ? (
                                            <FaCheck className='check'/>
                                          ) : (
                                            <IoCopy className='copyicon'/>
                                          )}
                                        </div>
                                        <div className=''>
                                          {part.firstWord}
                                        </div>                            
                                    </div>
                                    <SyntaxHighlighter
                                      language={part.firstWord}
                                      style={docco}
                                      className='x-container'
                                      customStyle={{
                                        fontSize: '14px',
                                        lineHeight: '1.5',
                                        maxWidth: '100%',
                                        wordBreak: 'break-word',
                                        overflowWrap: 'break-word',
                                        whiteSpace: 'pre-wrap',
                                        overflow: 'auto'
                                      }}
                                    >
                                      {part.content}
                                    </SyntaxHighlighter>
                                  </div>
                                ) : (
                                  <p>{part.content}</p>
                                )}
                              </React.Fragment>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className='inputbox'>        
              <input             
                  className="input"    
                  type="text"
                  value={input}
                  placeholder="Type your message…"
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => handler(e)}
              />
            </div>
        </div>
      </div>
      :null}

      <div className='iconbox' onClick={()=>setOpen(!open)}>
         <img alt="charimage" src={redashpng} className="icon" />
      </div>     
    </>
  )
}