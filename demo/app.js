const query = document.querySelector('#query');
const search = document.querySelector('#search');
const status = document.querySelector('#status');
const results = document.querySelector('#results');
const config = document.querySelector('#config');
const labels = { tfidf: 'TF-IDF lexical', minilm: 'MiniLM semantic', rrf: 'RRF hybrid', identifier_aware: 'Identifier-aware reranking' };

function text(node, value) { node.textContent = value; return node; }
function explain(row) {
  if (!row.explanation) return '';
  const e = row.explanation;
  const movement = row.rank_change ? ' · moved ' + (row.rank_change > 0 ? 'up ' : 'down ') + Math.abs(row.rank_change) + ' from RRF' : ' · same rank as RRF';
  const adjustment = Number(e.match_bonus || 0) - Number(e.conflict_penalty || 0);
  return 'match ' + (e.match_fraction || 0) + '; conflict ' + (e.conflict ? 'yes' : 'no') + '; adjustment ' + adjustment.toFixed(4) + movement;
}
function render(data) {
  results.replaceChildren();
  config.hidden = false;
  config.textContent = 'Frozen research configuration: MiniLM ' + data.configuration.model + '; RRF k=' + data.configuration.rrf_k + '; match=' + data.configuration.lambda_match + '; conflict=' + data.configuration.lambda_conflict + '; ' + data.configuration.corpus_documents + ' documents.';
  Object.entries(data.methods).forEach(function(pair) {
    const method = pair[0], rows = pair[1];
    const card = document.querySelector('#card').content.firstElementChild.cloneNode(true);
    text(card.querySelector('h2'), labels[method]);
    text(card.querySelector('span'), 'top ' + rows.length);
    const box = card.querySelector('.rows');
    rows.forEach(function(row) {
      const item = document.createElement('div'); item.className = 'result';
      const line = document.createElement('div');
      line.append(Object.assign(document.createElement('span'), { className:'rank', textContent:'#' + row.rank }));
      line.append(Object.assign(document.createElement('a'), { className:'title', textContent:row.title || row.doc_id, href:row.source_url, target:'_blank', rel:'noopener' }));
      item.append(line);
      item.append(Object.assign(document.createElement('p'), { className:'meta', textContent:row.doc_id + ' · score ' + row.score }));
      if (row.explanation) item.append(Object.assign(document.createElement('p'), { className:'explain', textContent:explain(row) }));
      box.append(item);
    });
    results.append(card);
  });
}
async function run() {
  search.disabled = true; status.textContent = 'Searching the real local corpus…';
  try {
    const response = await fetch('/api/search?q=' + encodeURIComponent(query.value) + '&top_k=5');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Search failed');
    render(data); status.textContent = 'Live result for: ' + data.query;
  } catch (error) { status.textContent = error.message; }
  finally { search.disabled = false; }
}
document.querySelectorAll('.sample').forEach(function(button) { button.addEventListener('click', function() { query.value = button.dataset.query; run(); }); });
search.addEventListener('click', run);
query.addEventListener('keydown', function(event) { if (event.key === 'Enter') run(); });
fetch('/api/health').then(function(r) { return r.json(); }).then(function(data) { status.textContent = 'Ready: ' + data.documents + ' documents; MiniLM embedding cache ' + (data.model_cache_hit ? 'hit' : 'built') + '.'; run(); }).catch(function() { status.textContent = 'Server is starting; try again in a moment.'; });
