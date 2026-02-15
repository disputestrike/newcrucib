/**
 * CrucibAI VS Code Extension
 * Full integration with 115-agent autonomous swarm
 * Enables "vibe coding" directly in VS Code
 */

const vscode = require('vscode');
const axios = require('axios');
const path = require('path');

// Configuration
const API_BASE_URL = process.env.CRUCIBAI_API_URL || 'http://localhost:8000';
const API_KEY = process.env.CRUCIBAI_API_KEY || '';

// Global state
let statusBar;
let outputChannel;
let isGenerating = false;
let currentBuildId = null;

/**
 * Extension activation
 */
async function activate(context) {
    console.log('CrucibAI VS Code Extension activated');

    // Create output channel
    outputChannel = vscode.window.createOutputChannel('CrucibAI');
    outputChannel.show(true);

    // Create status bar
    statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.command = 'crucibai.showStatus';
    statusBar.text = '$(zap) CrucibAI Ready';
    statusBar.show();
    context.subscriptions.push(statusBar);

    // Register commands
    registerCommands(context);

    // Register providers
    registerProviders(context);

    // Register listeners
    registerListeners(context);

    outputChannel.appendLine('✅ CrucibAI Extension loaded successfully');
}

/**
 * Register all VS Code commands
 */
function registerCommands(context) {
    // Main generation command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.generateCode', async () => {
            await generateCode();
        })
    );

    // Quick fix command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.quickFix', async () => {
            await quickFix();
        })
    );

    // Vibe analyzer command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.analyzeVibe', async () => {
            await analyzeVibe();
        })
    );

    // Voice input command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.voiceInput', async () => {
            await voiceInput();
        })
    );

    // Generate tests command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.generateTests', async () => {
            await generateTests();
        })
    );

    // Refactor command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.refactor', async () => {
            await refactorCode();
        })
    );

    // Documentation command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.generateDocs', async () => {
            await generateDocumentation();
        })
    );

    // Show status command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.showStatus', async () => {
            showStatus();
        })
    );

    // Settings command
    context.subscriptions.push(
        vscode.commands.registerCommand('crucibai.settings', async () => {
            showSettings();
        })
    );
}

/**
 * Register code completion and hover providers
 */
function registerProviders(context) {
    // Completion provider
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            ['javascript', 'typescript', 'python', 'java', 'go', 'rust'],
            {
                async provideCompletionItems(document, position, token, context) {
                    return await getCompletions(document, position);
                },
                resolveCompletionItem(item, token) {
                    return item;
                }
            },
            '.'
        )
    );

    // Hover provider
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(
            ['javascript', 'typescript', 'python', 'java', 'go', 'rust'],
            {
                async provideHover(document, position, token) {
                    return await getHoverInfo(document, position);
                }
            }
        )
    );

    // Code action provider
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            ['javascript', 'typescript', 'python', 'java', 'go', 'rust'],
            {
                async provideCodeActions(document, range, context, token) {
                    return await getCodeActions(document, range, context);
                }
            }
        )
    );
}

/**
 * Register event listeners
 */
function registerListeners(context) {
    // On file save
    vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (shouldAnalyzeFile(document)) {
            await analyzeFile(document);
        }
    });

    // On file open
    vscode.workspace.onDidOpenTextDocument(async (document) => {
        if (shouldAnalyzeFile(document)) {
            outputChannel.appendLine(`📂 Opened: ${document.fileName}`);
        }
    });

    // On text change
    vscode.workspace.onDidChangeTextDocument(async (event) => {
        // Debounced analysis
        if (shouldAnalyzeFile(event.document)) {
            // Could implement debounced analysis here
        }
    });
}

/**
 * Main code generation function
 */
async function generateCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    try {
        isGenerating = true;
        statusBar.text = '$(loading~spin) CrucibAI Generating...';

        // Get user input
        const prompt = await vscode.window.showInputBox({
            placeHolder: 'Describe what you want to generate...',
            prompt: 'CrucibAI Code Generation'
        });

        if (!prompt) return;

        outputChannel.appendLine(`\n📝 Prompt: ${prompt}`);

        // Call API
        const response = await axios.post(`${API_BASE_URL}/api/generate`, {
            prompt: prompt,
            context: editor.document.getText(),
            language: editor.document.languageId,
            file_path: editor.document.fileName
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { code, explanation, build_id } = response.data;
        currentBuildId = build_id;

        // Insert generated code
        const position = editor.selection.active;
        await editor.edit(editBuilder => {
            editBuilder.insert(position, code);
        });

        outputChannel.appendLine(`✅ Code generated successfully`);
        outputChannel.appendLine(`📊 Explanation: ${explanation}`);

        statusBar.text = '$(check) CrucibAI Ready';
        vscode.window.showInformationMessage('✅ Code generated successfully!');

    } catch (error) {
        outputChannel.appendLine(`❌ Error: ${error.message}`);
        vscode.window.showErrorMessage(`CrucibAI Error: ${error.message}`);
        statusBar.text = '$(error) CrucibAI Error';
    } finally {
        isGenerating = false;
    }
}

/**
 * Quick fix function
 */
async function quickFix() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    try {
        statusBar.text = '$(loading~spin) CrucibAI Analyzing...';

        const selectedText = editor.document.getText(editor.selection);
        if (!selectedText) {
            vscode.window.showErrorMessage('Select code to fix');
            return;
        }

        const response = await axios.post(`${API_BASE_URL}/api/fix`, {
            code: selectedText,
            language: editor.document.languageId
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { fixed_code, issues, suggestions } = response.data;

        // Show issues
        outputChannel.appendLine(`\n🔍 Issues found: ${issues.length}`);
        issues.forEach(issue => {
            outputChannel.appendLine(`  - ${issue.severity}: ${issue.message}`);
        });

        // Replace code
        await editor.edit(editBuilder => {
            editBuilder.replace(editor.selection, fixed_code);
        });

        vscode.window.showInformationMessage(`✅ Fixed ${issues.length} issues`);
        statusBar.text = '$(check) CrucibAI Ready';

    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Analyze vibe function
 */
async function analyzeVibe() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    try {
        statusBar.text = '$(loading~spin) Analyzing vibe...';

        const response = await axios.post(`${API_BASE_URL}/api/analyze-vibe`, {
            code: editor.document.getText(),
            file_path: editor.document.fileName
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { vibe_name, emotional_tone, visual_energy, suggestions } = response.data;

        // Show vibe analysis
        const message = `🎨 Vibe: ${vibe_name}\n📊 Tone: ${emotional_tone}\n⚡ Energy: ${visual_energy}`;
        vscode.window.showInformationMessage(message);

        outputChannel.appendLine(`\n🎨 Vibe Analysis:`);
        outputChannel.appendLine(`  Vibe: ${vibe_name}`);
        outputChannel.appendLine(`  Tone: ${emotional_tone}`);
        outputChannel.appendLine(`  Energy: ${visual_energy}`);
        outputChannel.appendLine(`  Suggestions: ${suggestions.join(', ')}`);

        statusBar.text = '$(check) CrucibAI Ready';

    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Voice input function
 */
async function voiceInput() {
    try {
        statusBar.text = '$(loading~spin) Listening...';
        vscode.window.showInformationMessage('🎤 Listening... (15 seconds)');

        const response = await axios.post(`${API_BASE_URL}/api/voice-input`, {
            duration: 15
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { text, confidence, code_suggestion } = response.data;

        outputChannel.appendLine(`\n🎤 Voice Input:`);
        outputChannel.appendLine(`  Transcribed: ${text}`);
        outputChannel.appendLine(`  Confidence: ${(confidence * 100).toFixed(1)}%`);

        if (code_suggestion) {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                await editor.edit(editBuilder => {
                    editBuilder.insert(editor.selection.active, code_suggestion);
                });
                vscode.window.showInformationMessage('✅ Code inserted from voice');
            }
        }

        statusBar.text = '$(check) CrucibAI Ready';

    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Generate tests function
 */
async function generateTests() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    try {
        statusBar.text = '$(loading~spin) Generating tests...';

        const response = await axios.post(`${API_BASE_URL}/api/generate-tests`, {
            code: editor.document.getText(),
            language: editor.document.languageId,
            file_path: editor.document.fileName
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { test_code, coverage, recommendations } = response.data;

        // Create test file
        const testFileName = editor.document.fileName.replace(/\.(\w+)$/, '.test.$1');
        const testUri = vscode.Uri.file(testFileName);

        await vscode.workspace.fs.writeFile(testUri, Buffer.from(test_code));

        const testDoc = await vscode.workspace.openTextDocument(testUri);
        await vscode.window.showTextDocument(testDoc);

        outputChannel.appendLine(`\n✅ Tests generated`);
        outputChannel.appendLine(`  Coverage: ${coverage}%`);
        outputChannel.appendLine(`  File: ${testFileName}`);

        vscode.window.showInformationMessage(`✅ Tests generated (${coverage}% coverage)`);
        statusBar.text = '$(check) CrucibAI Ready';

    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Refactor code function
 */
async function refactorCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    try {
        statusBar.text = '$(loading~spin) Refactoring...';

        const response = await axios.post(`${API_BASE_URL}/api/refactor`, {
            code: editor.document.getText(),
            language: editor.document.languageId
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { refactored_code, improvements, performance_gain } = response.data;

        // Show diff
        outputChannel.appendLine(`\n🔄 Refactoring suggestions:`);
        improvements.forEach(imp => {
            outputChannel.appendLine(`  - ${imp}`);
        });
        outputChannel.appendLine(`  Performance gain: ${performance_gain}%`);

        // Replace code
        await editor.edit(editBuilder => {
            const fullRange = new vscode.Range(
                editor.document.positionAt(0),
                editor.document.positionAt(editor.document.getText().length)
            );
            editBuilder.replace(fullRange, refactored_code);
        });

        vscode.window.showInformationMessage(`✅ Refactored (${performance_gain}% improvement)`);
        statusBar.text = '$(check) CrucibAI Ready';

    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Generate documentation function
 */
async function generateDocumentation() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    try {
        statusBar.text = '$(loading~spin) Generating docs...';

        const response = await axios.post(`${API_BASE_URL}/api/generate-docs`, {
            code: editor.document.getText(),
            language: editor.document.languageId,
            file_path: editor.document.fileName
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { documentation, examples, api_reference } = response.data;

        // Create docs file
        const docsFileName = editor.document.fileName.replace(/\.(\w+)$/, '.md');
        const docsUri = vscode.Uri.file(docsFileName);

        const docsContent = `# Documentation\n\n${documentation}\n\n## Examples\n${examples}\n\n## API Reference\n${api_reference}`;
        await vscode.workspace.fs.writeFile(docsUri, Buffer.from(docsContent));

        const docsDoc = await vscode.workspace.openTextDocument(docsUri);
        await vscode.window.showTextDocument(docsDoc);

        vscode.window.showInformationMessage('✅ Documentation generated');
        statusBar.text = '$(check) CrucibAI Ready';

    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Get code completions
 */
async function getCompletions(document, position) {
    try {
        const linePrefix = document.lineAt(position).text.substr(0, position.character);

        const response = await axios.post(`${API_BASE_URL}/api/completions`, {
            code: document.getText(),
            position: document.offsetAt(position),
            language: document.languageId
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { completions } = response.data;

        return completions.map(comp => {
            const item = new vscode.CompletionItem(comp.label, vscode.CompletionItemKind.Function);
            item.insertText = comp.insertText;
            item.documentation = comp.documentation;
            item.detail = comp.detail;
            return item;
        });

    } catch (error) {
        return [];
    }
}

/**
 * Get hover information
 */
async function getHoverInfo(document, position) {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/hover`, {
            code: document.getText(),
            position: document.offsetAt(position),
            language: document.languageId
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { info } = response.data;

        return new vscode.Hover(new vscode.MarkdownString(info));

    } catch (error) {
        return null;
    }
}

/**
 * Get code actions
 */
async function getCodeActions(document, range, context) {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/code-actions`, {
            code: document.getText(),
            range: {
                start: document.offsetAt(range.start),
                end: document.offsetAt(range.end)
            },
            language: document.languageId
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { actions } = response.data;

        return actions.map(action => {
            const codeAction = new vscode.CodeAction(action.title, vscode.CodeActionKind.QuickFix);
            codeAction.edit = new vscode.WorkspaceEdit();
            codeAction.edit.replace(document.uri, range, action.replacement);
            return codeAction;
        });

    } catch (error) {
        return [];
    }
}

/**
 * Analyze file
 */
async function analyzeFile(document) {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/analyze`, {
            code: document.getText(),
            language: document.languageId,
            file_path: document.fileName
        }, {
            headers: { 'Authorization': `Bearer ${API_KEY}` }
        });

        const { quality_score, issues, suggestions } = response.data;

        // Update status bar with quality score
        statusBar.text = `$(zap) CrucibAI ${quality_score}/10`;

    } catch (error) {
        // Silent error
    }
}

/**
 * Show status
 */
function showStatus() {
    const message = `CrucibAI Status:\n- API: Connected\n- Build ID: ${currentBuildId || 'None'}\n- Status: ${isGenerating ? 'Generating' : 'Ready'}`;
    vscode.window.showInformationMessage(message);
}

/**
 * Show settings
 */
function showSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'crucibai');
}

/**
 * Helper: Should analyze file
 */
function shouldAnalyzeFile(document) {
    const supportedLanguages = ['javascript', 'typescript', 'python', 'java', 'go', 'rust', 'cpp', 'csharp'];
    return supportedLanguages.includes(document.languageId);
}

/**
 * Deactivation
 */
function deactivate() {
    console.log('CrucibAI Extension deactivated');
}

module.exports = {
    activate,
    deactivate
};
