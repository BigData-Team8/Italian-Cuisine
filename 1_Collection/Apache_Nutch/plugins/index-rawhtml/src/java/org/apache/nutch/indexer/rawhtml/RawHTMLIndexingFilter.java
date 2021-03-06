/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.nutch.indexer.rawhtml;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import org.apache.nutch.metadata.Nutch;
import org.apache.nutch.parse.Parse;

import org.apache.nutch.indexer.IndexingFilter;
import org.apache.nutch.indexer.IndexingException;
import org.apache.nutch.indexer.NutchDocument
;import org.apache.nutch.util.StringUtil;
import org.apache.nutch.util.URLUtil;
import org.apache.hadoop.io.Text;

import org.apache.nutch.crawl.CrawlDatum;
import org.apache.nutch.crawl.Inlinks;

import org.apache.hadoop.conf.Configuration;

/**
 * Adds raw HTML to a document.
 * This plugin is linked to parse-rawhtml.
 */
public class RawHTMLIndexingFilter implements IndexingFilter {

  private static final Log LOG = LogFactory.getLog(RawHTMLIndexingFilter.class.getName());

  // we have no configuration entry for this plugin; nevertheless we keep it for further implementations
  private Configuration conf;

  public void setConf(Configuration conf) {
    this.conf = conf;
  }

  public Configuration getConf() {
    return this.conf;
  }

  public NutchDocument filter(NutchDocument doc, Parse parse, Text url, 
    CrawlDatum datum, Inlinks inlinks) throws IndexingException {

    LOG.info("plugin loaded!");

    doc.add("rawhtml", parse.getData().getMeta("rawhtml"));

    return doc;
  }
}
