%%
%% This is file `tubslttr2.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% ../tubsvers.inc  (with options: `default,extra')
%% tubslttr2.dtx  (with options: `class')
%% 
%% This is a generated file.
%% 
%% Copyright (C) 2011 by Tobias Rad and Enrico Jörns
%% 
%% This file may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either
%% version 1.2 of this license or (at your option) any later
%% version. The latest version of this license is in:
%% 
%%   http://www.latex-project.org/lppl.txt
%% 
%% and version 1.2 or later is part of all distributions of
%% LaTeX version 1999/12/01 or later.
%% 
\RequirePackage{ifthen}
\RequirePackage{scrlfile}%TODO: KOMA-Check?
\RequirePackage{etoolbox}%
\begingroup
  \makeatletter
  \ifx\tubslatexVersion\undefined
    \newcommand*{\check@tubslatexVersion}[1]{%
      \gdef\tubslatexVersion{#1}%
    }%
  \else
    \newcommand*{\check@tubslatexVersion}[1]{%
      \def\@tempa{#1}%
      \ifx\tubslatexVersion\@tempa\else
        \@latex@warning@no@line{%
          \noexpand\tubslatexVersion\space is
          `\tubslatexVersion',\MessageBreak
          but `#1' was expected!\MessageBreak
          You should not use classes, packages or files
          from\MessageBreak
          different tubslatex versions%
        }%
      \fi
    }
  \fi
  \check@tubslatexVersion{2024/02/22 v1.3.5-r140 tubslatex}%
\endgroup
\providecommand{\tubslatex}{tubs\LaTeX}
\AfterPackage*{ucs}{%
  \pretocmd{\author}{\PrerenderUnicode{ä,ö,ü,ß}}{}{}%
  \pretocmd{\title}{\PrerenderUnicode{ä,ö,ü,ß}}{}{}%
}
\AtBeginDocument{
  \@ifpackageloaded{hyperref}{%
    \@ifundefined{inputencodingname}{}{%
      \hypersetup{
        pdftitle = {\@title},
        pdfauthor = {\@author},
        pdfcreator = {\tubslatexVersion}
      }
    }
  }{}
}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{tubslttr2}[\tubslatexVersion\space TU Braunschweig letter class]
\RequirePackage{xkeyval}
\newif\ifarial\arialfalse
\RequirePackage{scrbase}
\newif\if@OldKomaVersion
\@ifpackagelater{scrbase}{2011/06/16}{%
  \PassOptionsToClass{%
    tubs,%
    BCOR=0cm,%
    pagenumber=botleft,%
    refline=nodate,%
    backaddress=plain%  Keine Linie unterhalb Rücksendeadresse
  }{scrlttr2}
  \@OldKomaVersionfalse
}{%
  \PassOptionsToClass{%
    tubs,%
    BCOR=0cm,%
    pagenumber=botleft,%
    backaddress=plain%  Keine Linie unterhalb Rücksendeadresse
  }{scrlttr2}
  \@OldKomaVersiontrue
}
\DeclareOptionX{mono}{%
  \PassOptionsToPackage{mono}{tubslogo}
  \PassOptionsToPackage{mono}{tubscolors}
}
\DeclareOptionX{arial}{%
  \PassOptionsToClass{fontsize=10pt}{scrlttr2}
  \arialtrue
}
\DeclareOptionX{nexus}{%
  \PassOptionsToClass{fontsize=11pt}{scrlttr2}
  \arialfalse
}
\DeclareOptionX*{\PassOptionsToClass{\CurrentOption}{scrlttr2}}
\ExecuteOptionsX{nexus}
\ProcessOptionsX
\LoadClass{scrlttr2}[2011/06/16]
\endinput
%%
%% End of file `tubslttr2.cls'.
